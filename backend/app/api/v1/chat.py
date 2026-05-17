import json

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.database import SessionLocal
from app.models.conversation import Conversation
from app.models.dataset import Dataset
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from app.services.metric_service import get_metrics_grouped
from app.services.insight_service import get_insights
from app.utils.file_parser import parse_file
from app.ai.chat_agent import RevenueAIChatAgent

router = APIRouter()


@router.post("/chat/{dataset_id}", response_model=ChatResponse)
def chat_with_dataset(
    dataset_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not dataset.file_path:
        raise HTTPException(
            status_code=400,
            detail="Dataset file not available. The data may have been cleaned up.",
        )

    df = parse_file(dataset.file_path)

    metrics_grouped = get_metrics_grouped(db, dataset_id)
    metrics_summary = _format_metrics_summary(metrics_grouped)

    conversation = (
        db.query(Conversation)
        .filter(Conversation.dataset_id == dataset_id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )

    if not conversation:
        conversation = Conversation(dataset_id=dataset_id, messages=[])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    agent = RevenueAIChatAgent(
        df=df,
        messages=conversation.messages or [],
        metadata={
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns_meta": dataset.columns_meta or [],
            "metrics_summary": metrics_summary,
        },
    )

    reply = agent.chat(request.message)

    conversation.messages = agent.get_messages()
    db.commit()

    return ChatResponse(
        reply=reply,
        conversation_id=conversation.id,
        insights=None,
    )


@router.get("/conversations/{dataset_id}", response_model=ConversationResponse)
def get_conversation(dataset_id: str, db: Session = Depends(get_db)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.dataset_id == dataset_id)
        .order_by(Conversation.updated_at.desc())
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404, detail="No conversation found for this dataset"
        )

    return conversation


def _format_metrics_summary(metrics_grouped: dict) -> str:
    lines = []
    for mtype, metrics in metrics_grouped.items():
        if not metrics:
            continue
        label = mtype.replace("_", " ").title()
        samples = metrics[:3]
        vals = []
        for m in samples:
            v = m.value
            p = m.period
            if p and p != "all":
                vals.append(f"{m.metric_name}: {v:,.2f} ({p})" if isinstance(v, (int, float)) else f"{m.metric_name}: {v} ({p})")
            else:
                vals.append(f"{m.metric_name}: {v:,.2f}" if isinstance(v, (int, float)) else f"{m.metric_name}: {v}")
        lines.append(f"{label}: {'; '.join(vals)}")
    return "\n".join(lines)


@router.websocket("/ws/chat/{dataset_id}")
async def websocket_chat(websocket: WebSocket, dataset_id: str):
    await websocket.accept()

    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            await websocket.send_json({"type": "error", "content": "Dataset not found"})
            await websocket.close(code=4004)
            return

        if not dataset.file_path:
            await websocket.send_json(
                {"type": "error", "content": "Dataset file not available"}
            )
            await websocket.close(code=4004)
            return

        df = parse_file(dataset.file_path)

        metrics_grouped = get_metrics_grouped(db, dataset_id)
        metrics_summary = _format_metrics_summary(metrics_grouped)

        conversation = (
            db.query(Conversation)
            .filter(Conversation.dataset_id == dataset_id)
            .order_by(Conversation.updated_at.desc())
            .first()
        )

        if not conversation:
            conversation = Conversation(dataset_id=dataset_id, messages=[])
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        agent = RevenueAIChatAgent(
            df=df,
            messages=conversation.messages or [],
            metadata={
                "name": dataset.name,
                "row_count": dataset.row_count,
                "column_count": dataset.column_count,
                "columns_meta": dataset.columns_meta or [],
                "metrics_summary": metrics_summary,
            },
        )

        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "content": "Invalid JSON message"}
                )
                continue

            if data.get("type") != "message":
                continue

            question = (data.get("content") or "").strip()
            if not question:
                continue

            for chunk in agent.stream_chat(question):
                await websocket.send_json(chunk)

            conversation.messages = agent.get_messages()
            db.commit()

            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
    finally:
        db.close()

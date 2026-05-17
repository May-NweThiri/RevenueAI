from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    insights: list[dict] | None = None


class ConversationResponse(BaseModel):
    id: str
    dataset_id: str
    messages: list[ChatMessage] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

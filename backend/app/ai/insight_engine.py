import json
from typing import Any

from openai import OpenAI

from app.ai.prompts import INSIGHT_SYSTEM_PROMPT, INSIGHT_USER_PROMPT, CHAT_SYSTEM_PROMPT, CHAT_USER_PROMPT
from app.config import settings


def _metrics_to_summary(metrics_grouped: dict) -> str:
    lines = []
    for metric_type, metrics in metrics_grouped.items():
        if not metrics:
            continue
        lines.append(f"\n{metric_type.replace('_', ' ').title()}:")
        for m in metrics[:5]:
            val = m.get("value", "N/A")
            period = m.get("period", "")
            name = m.get("metric_name", "")
            if period and period != "all":
                lines.append(f"  - {name}: ${val:,.2f}" if isinstance(val, (int, float)) else f"  - {name}: {val}")
            else:
                lines.append(f"  - {name}: ${val:,.2f}" if isinstance(val, (int, float)) else f"  - {name}: {val}")
    return "\n".join(lines)


def _columns_to_info(columns_meta: list[dict]) -> str:
    lines = []
    for c in columns_meta:
        role = c.get("detected_role", "unknown")
        lines.append(f"  - {c['name']} ({c['dtype']}) → {role}")
    return "\n".join(lines)


def generate_insights(
    dataset_name: str,
    row_count: int,
    column_count: int,
    columns_meta: list[dict],
    metrics_grouped: dict,
) -> list[dict]:
    if not settings.OPENAI_API_KEY:
        return _generate_fallback_insights(metrics_grouped)

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        user_prompt = INSIGHT_USER_PROMPT.format(
            dataset_name=dataset_name,
            row_count=row_count,
            column_count=column_count,
            columns_info=_columns_to_info(columns_meta),
            metrics_summary=_metrics_to_summary(metrics_grouped),
        )

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            response_format={"type": "json_object"},
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

        content = response.choices[0].message.content
        if content:
            data = json.loads(content)
            insights = data.get("insights", data.get("results", []))
            if isinstance(insights, list) and len(insights) > 0:
                return insights

    except Exception:
        pass

    return _generate_fallback_insights(metrics_grouped)


def _generate_fallback_insights(metrics_grouped: dict) -> list[dict]:
    insights = []

    total_rev = metrics_grouped.get("total_revenue", [])
    if total_rev:
        val = total_rev[0].get("value", 0)
        insights.append({
            "type": "trend",
            "title": f"Total revenue is ${val:,.2f}",
            "content": f"The dataset shows total revenue of ${val:,.2f}. "
                       f"This represents the overall business volume across the analyzed period.",
            "severity": "info",
        })

    growth = metrics_grouped.get("growth_rate", [])
    for g in growth:
        if g.get("period") == "all" and g.get("value") is not None:
            val = g["value"]
            if val > 20:
                sev = "info"
                msg = f"Strong growth of {val:.1f}% indicates the business is scaling effectively."
            elif val > 0:
                sev = "info"
                msg = f"Positive growth of {val:.1f}% shows steady business expansion."
            elif val > -10:
                sev = "warning"
                msg = f"Negative growth of {val:.1f}% suggests a need for strategic review."
            else:
                sev = "critical"
                msg = f"Significant decline of {val:.1f}% requires immediate attention."
            insights.append({
                "type": "trend" if val >= 0 else "decline",
                "title": f"Growth rate is {val:+.1f}%",
                "content": msg,
                "severity": sev,
            })
            break

    aov = metrics_grouped.get("aov", [])
    if aov:
        val = aov[0].get("value", 0)
        insights.append({
            "type": "opportunity",
            "title": f"Average order value is ${val:,.2f}",
            "content": f"The average order value is ${val:,.2f}. "
                       f"Consider upselling and bundling strategies to increase this metric.",
            "severity": "info",
        })

    anomalies = metrics_grouped.get("trends", [])
    anomaly_items = [t for t in anomalies if t.get("metadata", {}).get("type") == "anomaly"]
    for a in anomaly_items[:2]:
        insights.append({
            "type": "anomaly",
            "title": f"Anomaly detected in {a.get('period', 'unknown period')}",
            "content": f"Revenue of ${a.get('value', 0):,.2f} in {a.get('period', 'unknown')} "
                       f"deviates significantly from the trend (z-score: {a.get('metadata', {}).get('z_score', 'N/A')}).",
            "severity": "warning",
        })

    top_products = metrics_grouped.get("top_products", [])
    if top_products:
        top = top_products[0]
        insights.append({
            "type": "recommendation",
            "title": f"Top product: {top.get('metric_name', 'N/A')}",
            "content": f"'{top.get('metric_name', 'N/A')}' leads with ${top.get('value', 0):,.2f} in revenue. "
                       f"Consider increasing marketing investment in this product line.",
            "severity": "info",
        })

    return insights


def generate_chat_response(
    user_message: str,
    dataset_name: str,
    row_count: int,
    column_count: int,
    columns_meta: list[dict],
    metrics_grouped: dict,
    insights: list[dict],
    chat_history: list[dict],
) -> str:
    if not settings.OPENAI_API_KEY:
        return _generate_fallback_chat_response(user_message, metrics_grouped)

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        column_roles = "\n".join(
            f"  - {c['name']} → {c.get('detected_role', 'unknown')}"
            for c in columns_meta
        )

        insights_summary = "\n".join(
            f"  - [{i.get('type', 'general')}] {i.get('title', '')}"
            for i in insights[:5]
        )

        chat_history_text = "\n".join(
            f"{m.get('role', 'user')}: {m.get('content', '')}"
            for m in chat_history[-6:]
        )

        user_prompt = CHAT_USER_PROMPT.format(
            dataset_name=dataset_name,
            row_count=row_count,
            column_count=column_count,
            column_roles=column_roles,
            metrics_summary=_metrics_to_summary(metrics_grouped),
            insights_summary=insights_summary,
            chat_history=chat_history_text,
            user_message=user_message,
        )

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

        return response.choices[0].message.content or "I couldn't generate a response. Please try again."

    except Exception as e:
        return f"I encountered an error while processing your question: {str(e)}"


def _generate_fallback_chat_response(user_message: str, metrics_grouped: dict) -> str:
    user_lower = user_message.lower()

    total_rev = metrics_grouped.get("total_revenue", [])
    growth = metrics_grouped.get("growth_rate", [])
    aov = metrics_grouped.get("aov", [])
    top_products = metrics_grouped.get("top_products", [])

    if "revenue" in user_lower or "sales" in user_lower or "total" in user_lower:
        if total_rev:
            val = total_rev[0].get("value", 0)
            return f"The total revenue is **${val:,.2f}**."
        return "I don't have revenue data to answer that. Please check your dataset has a revenue column."

    if "growth" in user_lower or "trend" in user_lower:
        for g in growth:
            if g.get("period") == "all":
                return f"The overall growth rate is **{g['value']:+.1f}%**."
        return "I need at least two periods of data to calculate growth rates."

    if "product" in user_lower or "top" in user_lower or "best" in user_lower:
        if top_products:
            lines = [f"**Top Products:**"]
            for p in top_products[:5]:
                lines.append(f"  {p['rank']}. {p['metric_name']} — ${p['value']:,.2f}")
            return "\n".join(lines)
        return "No product data found in this dataset."

    if "aov" in user_lower or "average order" in user_lower:
        if aov:
            return f"The average order value is **${aov[0]['value']:,.2f}**."
        return "Could not calculate AOV. Revenue or quantity columns may be missing."

    if total_rev:
        val = total_rev[0].get("value", 0)
        return f"The dataset shows total revenue of **${val:,.2f}**. What specific analysis would you like me to perform?"

    return "I've analyzed your dataset. Could you ask a more specific question about revenue, products, or trends?"

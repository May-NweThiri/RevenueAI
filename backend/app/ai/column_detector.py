import json
import re
from typing import Any

import pandas as pd

from app.ai.prompts import COLUMN_DETECTION_SYSTEM_PROMPT, COLUMN_DETECTION_USER_PROMPT
from app.config import settings


REVENUE_KEYWORDS = [
    "revenue", "sales", "income", "amount", "total", "earnings",
    "turnover", "proceeds", "receipts", "gross", "net_sales",
    "transaction_amount", "order_amount", "invoice_amount",
    "payment", "received", "billing",
]

QUANTITY_KEYWORDS = ["qty", "quantity", "count", "units", "volume", "number_of", "num_"]

PRICE_KEYWORDS = [
    "price", "rate", "unit_price", "cost_per", "amount_per",
    "selling_price", "list_price", "standard_price",
]

DATE_KEYWORDS = [
    "date", "time", "timestamp", "created_at", "updated_at",
    "order_date", "transaction_date", "month", "year", "period",
    "day", "week", "quarter",
]

CATEGORY_KEYWORDS = [
    "category", "type", "group", "segment", "channel", "region",
    "department", "class", "status", "stage", "tier",
]

PRODUCT_KEYWORDS = [
    "product", "item", "sku", "name", "description", "service",
    "product_name", "product_id",
]

CUSTOMER_KEYWORDS = [
    "customer", "client", "buyer", "user", "account", "contact",
    "company", "organization",
]

DISCOUNT_KEYWORDS = ["discount", "promo", "coupon", "offer", "concession"]

COST_KEYWORDS = ["cost", "cogs", "expense", "spend", "spent", "cost_price"]

ID_KEYWORDS = ["id", "code", "key", "identifier", "reference", "order_id", "transaction_id"]


def _heuristic_detect(column_name: str, dtype: str, sample_values: list[Any]) -> str:
    col_lower = column_name.lower().replace("_", " ").replace("-", " ")

    for kw in ID_KEYWORDS:
        if kw in col_lower:
            return "id"

    for kw in DATE_KEYWORDS:
        if kw in col_lower:
            return "date"

    if dtype == "datetime64[ns]" or "datetime" in dtype:
        return "date"

    for kw in REVENUE_KEYWORDS:
        if kw in col_lower:
            return "revenue"

    for kw in PRICE_KEYWORDS:
        if kw in col_lower:
            return "unit_price"

    for kw in QUANTITY_KEYWORDS:
        if kw in col_lower:
            return "quantity"

    for kw in DISCOUNT_KEYWORDS:
        if kw in col_lower:
            return "discount"

    for kw in COST_KEYWORDS:
        if kw in col_lower:
            return "cost"

    for kw in PRODUCT_KEYWORDS:
        if kw in col_lower:
            return "product"

    for kw in CUSTOMER_KEYWORDS:
        if kw in col_lower:
            return "customer"

    for kw in CATEGORY_KEYWORDS:
        if kw in col_lower:
            return "category"

    numeric_samples = [v for v in sample_values if isinstance(v, (int, float))]
    str_samples = [str(v) for v in sample_values if v is not None]

    if numeric_samples:
        all_positive = all(v > 0 for v in numeric_samples if v is not None)
        if all_positive:
            has_large = any(v > 1000 for v in numeric_samples if v is not None)
            if has_large:
                return "revenue"

    if str_samples:
        unique_ratio = len(set(str_samples)) / max(len(str_samples), 1)
        if unique_ratio < 0.3 and len(str_samples) > 5:
            return "category"

    return "other"


def _is_date_column(series: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(series):
        return False
    sample = series.dropna().head(20)
    if len(sample) < 2:
        return False
    try:
        parsed = pd.to_datetime(sample, errors="coerce")
        success_rate = parsed.notna().sum() / len(sample)
        return success_rate > 0.7
    except (ValueError, TypeError, OverflowError):
        return False


def _get_sample_values(df: pd.DataFrame, col: str, n: int = 5) -> list:
    values = df[col].dropna().head(n).tolist()
    return [str(v) if not isinstance(v, (int, float)) else v for v in values]


def detect_columns(df: pd.DataFrame) -> list[dict]:
    columns_meta = []

    for col in df.columns:
        dtype = str(df[col].dtype)
        sample_values = _get_sample_values(df, col)

        if "datetime" in dtype or _is_date_column(df[col]):
            role = "date"
            confidence = "high"
            reason = "Detected as date/time column"
        else:
            role = _heuristic_detect(col, dtype, sample_values)
            confidence = "medium"
            reason = f"Heuristic match based on column name and values"

        columns_meta.append({
            "name": col,
            "dtype": dtype,
            "detected_role": role,
            "confidence": confidence,
            "reason": reason,
            "sample_values": sample_values[:3],
        })

    revenue_cols = [c for c in columns_meta if c["detected_role"] == "revenue"]
    if not revenue_cols:
        numeric_cols = [c for c in columns_meta if "int" in c["dtype"] or "float" in c["dtype"]]
        for col_meta in numeric_cols:
            if col_meta["detected_role"] == "other":
                series = df[col_meta["name"]]
                if series.nunique() > 5 and series.min() >= 0:
                    col_meta["detected_role"] = "revenue"
                    col_meta["confidence"] = "low"
                    col_meta["reason"] = "Fallback: best candidate revenue column"

    if settings.OPENAI_API_KEY:
        try:
            ai_roles = _detect_with_ai(df, columns_meta)
            if ai_roles:
                for meta in columns_meta:
                    if meta["name"] in ai_roles:
                        ai_role = ai_roles[meta["name"]]
                        if ai_role != "other":
                            meta["detected_role"] = ai_role
                            meta["confidence"] = "high"
                            meta["reason"] = f"AI confirmed: {ai_role}"
        except Exception:
            pass

    return columns_meta


def _detect_with_ai(df: pd.DataFrame, heuristic_results: list[dict]) -> dict | None:
    from openai import OpenAI

    columns_sample = {}
    for meta in heuristic_results:
        col = meta["name"]
        samples = df[col].dropna().head(5).tolist()
        columns_sample[col] = {
            "dtype": meta["dtype"],
            "sample_values": [str(s) if not isinstance(s, (int, float)) else s for s in samples],
            "heuristic_role": meta["detected_role"],
        }

    prompt = COLUMN_DETECTION_USER_PROMPT.format(
        columns_sample=json.dumps(columns_sample, indent=2)
    )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": COLUMN_DETECTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
        max_tokens=settings.OPENAI_MAX_TOKENS,
    )

    content = response.choices[0].message.content
    if content:
        try:
            data = json.loads(content)
            classifications = data.get("classifications", data.get("columns", data.get("results", [])))
            if isinstance(classifications, list):
                return {c["column_name"]: c["role"] for c in classifications if "column_name" in c and "role" in c}
            elif isinstance(classifications, dict):
                return classifications
        except json.JSONDecodeError:
            pass

    return None

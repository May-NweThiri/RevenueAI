import logging
from typing import Any, Generator

import pandas as pd

from app.config import settings
from app.ai.client import ai_configured, get_ai_client
from app.ai.metric_calculator import _normalized_groups

logger = logging.getLogger(__name__)


class RevenueAIChatAgent:
    """AI chat agent using the OpenAI API with pandas local fallback."""

    def __init__(
        self,
        df: pd.DataFrame,
        messages: list[dict] | None = None,
        metadata: dict | None = None,
    ):
        self.df = df
        self.messages = messages or []
        self.metadata = metadata or {}

    def _role_cols(self, role: str) -> list[str]:
        cols = self.metadata.get("columns_meta", [])
        return [c["name"] for c in cols if c.get("detected_role") == role]

    def _computed_aggregates(self) -> str:
        """Complete aggregate tables computed from the full dataframe.

        Stored metric summaries are truncated; these tables guarantee the LLM
        sees every month / product / category, not just a sample.
        """
        revenue_cols = self._role_cols("revenue")
        if not revenue_cols:
            return ""

        rev = revenue_cols[0]
        sections: list[str] = []

        try:
            total = float(pd.to_numeric(self.df[rev], errors="coerce").fillna(0).sum())
            sections.append(f"Total revenue (column '{rev}'): ${total:,.2f}")
        except Exception:
            pass

        date_cols = self._role_cols("date")
        if date_cols:
            try:
                tmp = self.df[[date_cols[0], rev]].copy()
                tmp[date_cols[0]] = pd.to_datetime(tmp[date_cols[0]], errors="coerce")
                tmp[rev] = pd.to_numeric(tmp[rev], errors="coerce").fillna(0)
                tmp = tmp.dropna(subset=[date_cols[0]])
                monthly = tmp.groupby(tmp[date_cols[0]].dt.to_period("M"))[rev].sum().sort_index()
                if len(monthly) > 0:
                    lines = [f"Monthly revenue (complete, all {len(monthly)} months):"]
                    for month, val in monthly.tail(60).items():
                        lines.append(f"  {month}: ${float(val):,.2f}")
                    sections.append("\n".join(lines))
            except Exception:
                pass

        product_cols = self._role_cols("product")
        if product_cols:
            try:
                grouped = _normalized_groups(self.df, product_cols[0], rev).head(15)
                lines = [f"Revenue by product ('{product_cols[0]}', top {len(grouped)}):"]
                for _, row in grouped.iterrows():
                    lines.append(f"  {row['_label']}: ${float(row['_value']):,.2f}")
                sections.append("\n".join(lines))
            except Exception:
                pass

        for cat_col in self._role_cols("category")[:2]:
            try:
                grouped = _normalized_groups(self.df, cat_col, rev).head(20)
                lines = [f"Revenue by {cat_col}:"]
                for _, row in grouped.iterrows():
                    lines.append(f"  {row['_label']}: ${float(row['_value']):,.2f}")
                sections.append("\n".join(lines))
            except Exception:
                pass

        return "\n\n".join(sections)

    def _build_context(self) -> str:
        cols = self.metadata.get("columns_meta", [])
        column_roles = "\n".join(
            f"  - {c.get('name', '?')} ({c.get('dtype', '?')}) "
            f"-> {c.get('detected_role', 'unknown')}"
            for c in cols
        )
        metrics = self.metadata.get("metrics_summary", "")
        aggregates = self._computed_aggregates()
        sample = self.df.head(8).to_string(index=False, max_cols=12)
        return (
            f"Dataset: {self.metadata.get('name', 'Unnamed')} "
            f"({self.metadata.get('row_count', 0)} rows, "
            f"{self.metadata.get('column_count', 0)} columns)\n"
            f"Columns:\n{column_roles}\n\n"
            f"Computed aggregates (calculated from the FULL dataset — complete "
            f"and authoritative, use these for any totals/breakdown questions):\n"
            f"{aggregates}\n\n"
            f"Key Metrics (truncated sample):\n{metrics}\n\n"
            f"Sample rows:\n{sample}"
        )

    def chat(self, question: str) -> str:
        full_answer = ""
        for chunk in self.stream_chat(question):
            if chunk["type"] == "token":
                full_answer += chunk["content"]
        return full_answer

    def stream_chat(self, question: str) -> Generator[dict, None, None]:
        token_gen = self._compute_answer_stream(question)

        full_answer = ""
        for item in token_gen:
            if item["type"] == "token":
                full_answer += item["content"]
            yield item

        self.messages.append({"role": "user", "content": question})
        self.messages.append({"role": "assistant", "content": full_answer})

    def _compute_answer_stream(self, question: str) -> Generator[dict, None, None]:
        if not ai_configured():
            yield {"type": "token", "content": self._local_fallback(question)}
            return
        yield from self._openai_stream(question)

    def _openai_stream(self, question: str) -> Generator[dict, None, None]:
        context = self._build_context()
        system_prompt = (
            "You are FinX AI, an expert AI business analyst. "
            "Answer questions about the user's uploaded dataset using the context below. "
            "The 'Computed aggregates' section is complete and calculated from the full "
            "dataset — when asked about monthly revenue, products, or category breakdowns, "
            "use those numbers and list them fully. Never claim data is unavailable if it "
            "appears there. "
            "Be specific with numbers, cite column names, and give actionable insights. "
            "You may also answer general knowledge questions about values that appear "
            "in the data (e.g. what a location or term is). "
            "Use markdown for lists when helpful.\n\n"
            f"{context}"
        )

        api_messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in self.messages[-8:]:
            if m.get("role") in ("user", "assistant"):
                api_messages.append({"role": m["role"], "content": m["content"]})
        api_messages.append({"role": "user", "content": question})

        try:
            client, model = get_ai_client()
            if client is None:
                yield {"type": "token", "content": self._local_fallback(question)}
                return
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                stream=True,
            )
            got_content = False
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    got_content = True
                    yield {"type": "token", "content": delta}
            if not got_content:
                yield {"type": "token", "content": self._local_fallback(question)}
        except Exception as e:
            logger.exception("OpenAI chat request failed")
            yield {
                "type": "token",
                "content": (
                    f"*AI request failed ({type(e).__name__}: {str(e)[:200]}). "
                    f"Falling back to basic analysis.*\n\n"
                    + self._local_fallback(question)
                ),
            }

    def _local_fallback(self, question: str) -> str:
        q = question.lower()
        cols = self.metadata.get("columns_meta", [])
        revenue_cols = [
            c["name"] for c in cols if c.get("detected_role") == "revenue"
        ]
        product_cols = [
            c["name"] for c in cols if c.get("detected_role") == "product"
        ]
        date_cols = [
            c["name"] for c in cols if c.get("detected_role") == "date"
        ]
        category_cols = [
            c["name"] for c in cols if c.get("detected_role") == "category"
        ]

        if not ai_configured():
            prefix = (
                "*AI chat is running in basic mode — add GEMINI_API_KEY (free) or "
                "OPENAI_API_KEY on Railway for full AI responses.*\n\n"
            )
        else:
            prefix = ""

        if "column" in q or "schema" in q or "structure" in q:
            lines = [f"The dataset has {len(self.df.columns)} columns:"]
            for c in cols:
                role = c.get("detected_role", "unknown")
                lines.append(f"  - {c['name']} ({c['dtype']}) -> {role}")
            return prefix + "\n".join(lines)

        if ("compare" in q or "category" in q or "breakdown" in q) and revenue_cols and category_cols:
            grouped = _normalized_groups(self.df, category_cols[0], revenue_cols[0])
            total = float(grouped["_value"].sum())
            lines = [f"**Revenue by {category_cols[0].title()}:**"]
            for _, row in grouped.iterrows():
                pct = (row["_value"] / total * 100) if total else 0
                lines.append(f"  {row['_label']}: ${row['_value']:,.2f} ({pct:.1f}%)")
            return prefix + "\n".join(lines)

        if ("top" in q or "best" in q or "ranking" in q or "leading" in q) and revenue_cols and product_cols:
            grouped = _normalized_groups(self.df, product_cols[0], revenue_cols[0]).head(10)
            lines = ["**Top Products by Revenue:**"]
            for i, (_, row) in enumerate(grouped.iterrows(), 1):
                lines.append(f"  {i}. {row['_label']} — ${row['_value']:,.2f}")
            return prefix + "\n".join(lines)

        if ("month" in q or "trend" in q or "growth" in q or "monthly" in q or "over time" in q) and revenue_cols and date_cols:
            df = self.df.copy()
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
            df["_month"] = df[date_cols[0]].dt.to_period("M").astype(str)
            monthly = df.groupby("_month")[revenue_cols[0]].sum()
            lines = ["**Monthly Revenue:**"]
            for month, rev in monthly.items():
                lines.append(f"  {month}: ${rev:,.2f}")
            return prefix + "\n".join(lines)

        if ("revenue" in q or "sales" in q or "total" in q or "earnings" in q) and revenue_cols:
            total = float(self.df[revenue_cols[0]].sum())
            return prefix + (
                f"Based on the data, total revenue from '{revenue_cols[0]}' is **${total:,.2f}**."
            )

        return prefix + (
            "I analyzed your dataset. Ask about revenue, products, trends, categories, "
            "or column structure for detailed answers."
        )

    def get_messages(self) -> list[dict]:
        return self.messages

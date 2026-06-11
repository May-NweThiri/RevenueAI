from typing import Any, Generator

import pandas as pd

from app.config import settings


class RevenueAIChatAgent:
    """AI chat agent using LangChain OpenAI with pandas local fallback."""

    def __init__(
        self,
        df: pd.DataFrame,
        messages: list[dict] | None = None,
        metadata: dict | None = None,
    ):
        self.df = df
        self.messages = messages or []
        self.metadata = metadata or {}
        self._llm = None

    def _get_llm(self):
        if self._llm is None and settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                api_key=settings.OPENAI_API_KEY,
            )
        return self._llm

    def _build_context(self) -> str:
        cols = self.metadata.get("columns_meta", [])
        column_roles = "\n".join(
            f"  - {c.get('name', '?')} ({c.get('dtype', '?')}) "
            f"-> {c.get('detected_role', 'unknown')}"
            for c in cols
        )
        metrics = self.metadata.get("metrics_summary", "")
        sample = self.df.head(8).to_string(index=False, max_cols=12)
        return (
            f"Dataset: {self.metadata.get('name', 'Unnamed')} "
            f"({self.metadata.get('row_count', 0)} rows, "
            f"{self.metadata.get('column_count', 0)} columns)\n"
            f"Columns:\n{column_roles}\n\n"
            f"Key Metrics:\n{metrics}\n\n"
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
        yield from self._langchain_stream(question)

    def _langchain_stream(self, question: str) -> Generator[dict, None, None]:
        llm = self._get_llm()
        if llm is None:
            yield {"type": "token", "content": self._local_fallback(question)}
            return

        context = self._build_context()
        system_prompt = (
            "You are RevenueAI, an expert AI business analyst. "
            "Answer questions about the user's uploaded dataset using the context below. "
            "Be specific with numbers, cite column names, and give actionable insights. "
            "Format currency as dollars. Use markdown for lists when helpful.\n\n"
            f"{context}"
        )

        try:
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        except ImportError:
            yield {"type": "token", "content": self._local_fallback(question)}
            return

        lc_messages = [SystemMessage(content=system_prompt)]
        for m in self.messages[-8:]:
            if m["role"] == "user":
                lc_messages.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                lc_messages.append(AIMessage(content=m["content"]))
        lc_messages.append(HumanMessage(content=question))

        try:
            for chunk in llm.stream(lc_messages):
                if chunk.content:
                    yield {"type": "token", "content": chunk.content}
        except Exception:
            yield {"type": "token", "content": self._local_fallback(question)}

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

        if not settings.OPENAI_API_KEY:
            prefix = (
                "*AI chat is running in basic mode — add OPENAI_API_KEY on Railway "
                "for full AI responses.*\n\n"
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
            grouped = self.df.groupby(category_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
            total = float(grouped.sum())
            lines = [f"**Revenue by {category_cols[0].title()}:**"]
            for cat, rev in grouped.items():
                pct = (rev / total * 100) if total else 0
                lines.append(f"  {cat}: ${rev:,.2f} ({pct:.1f}%)")
            return prefix + "\n".join(lines)

        if ("top" in q or "best" in q or "ranking" in q or "leading" in q) and revenue_cols and product_cols:
            grouped = self.df.groupby(product_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
            lines = ["**Top Products by Revenue:**"]
            for i, (prod, rev) in enumerate(grouped.head(10).items(), 1):
                lines.append(f"  {i}. {prod} — ${rev:,.2f}")
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

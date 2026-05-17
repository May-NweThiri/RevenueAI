from typing import Any, Generator

import pandas as pd

from app.config import settings


PANDASAI_GENERATE_CODE_PROMPT = """You are RevenueAI, an AI business analyst. You have access to a pandas DataFrame.

Dataset: {dataset_name} ({row_count} rows, {column_count} columns)
Columns and their detected roles:
{column_roles}

{previous_conversation}

The user's question is: {question}

Write Python pandas code to answer this question.
Rules:
- df is the variable name of the DataFrame
- Use df.columns to see available columns
- Do not use df.head() unless specifically asked
- Handle NaN values appropriately (use .fillna(0) or .dropna() as needed)
- Format monetary values as dollars
- Include percentages where relevant
- Print clear, formatted output
- If the question is ambiguous, make a reasonable assumption and explain it"""


class RevenueAIChatAgent:
    """AI chat agent combining PandasAI and LangChain for data analysis.

    PandasAI handles natural language -> pandas code generation + execution
    against the uploaded DataFrame for precise quantitative answers.

    LangChain provides structured fallback generation when PandasAI cannot
    process a query, using its ChatOpenAI model with conversation context.

    Flow:
        1. LangChain enriches the question with dataset context
        2. PandasAI generates pandas code, executes against the DataFrame
        3. If PandasAI fails, LangChain ChatOpenAI provides a fallback answer
        4. If neither API key is available, local template fallback is used
        5. Conversation state is synced for DB persistence
    """

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

        self._init_pandasai()
        self._restore_conversation()

    def _get_llm(self):
        if self._llm is None and settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                api_key=settings.OPENAI_API_KEY,
            )
        return self._llm

    def _init_pandasai(self):
        if not settings.OPENAI_API_KEY:
            self.pandasai = None
            return

        try:
            from pandasai import Agent as PandasAIAgent
            from pandasai.llm.openai import OpenAI as PandasAILLM
        except ImportError:
            self.pandasai = None
            return

        pandasai_llm = PandasAILLM(api_token=settings.OPENAI_API_KEY)
        self.pandasai = PandasAIAgent(
            [self.df],
            config={
                "llm": pandasai_llm,
                "enable_cache": False,
                "verbose": False,
                "save_logs": True,
                "custom_prompts": {
                    "generate_python_code": PANDASAI_GENERATE_CODE_PROMPT,
                },
            },
            memory_size=50,
        )

    def _restore_conversation(self):
        if self.pandasai is None:
            return
        mem = self.pandasai.context.memory
        for msg in self.messages:
            mem.add(msg["content"], msg["role"] == "user")

    def _build_context(self) -> str:
        cols = self.metadata.get("columns_meta", [])
        column_roles = "\n".join(
            f"  - {c.get('name', '?')} ({c.get('dtype', '?')}) "
            f"-> {c.get('detected_role', 'unknown')}"
            for c in cols
        )
        metrics = self.metadata.get("metrics_summary", "")
        return (
            f"Dataset: {self.metadata.get('name', 'Unnamed')} "
            f"({self.metadata.get('row_count', 0)} rows, "
            f"{self.metadata.get('column_count', 0)} columns)\n"
            f"Columns:\n{column_roles}\n\n"
            f"Key Metrics:\n{metrics}"
        )

    def _enrich_question(self, question: str) -> str:
        context = self._build_context()
        return (
            f"Dataset Context:\n{context}\n\n"
            f"Conversation History: "
            f"{len([m for m in self.messages if m['role'] == 'user'])} "
            f"previous questions asked.\n\n"
            f"Question: {question}"
        )

    def chat(self, question: str) -> str:
        full_answer = ""
        for chunk in self.stream_chat(question):
            full_answer += chunk["content"]
        return full_answer

    def stream_chat(self, question: str) -> Generator[dict, None, None]:
        enriched = self._enrich_question(question)

        token_gen = self._compute_answer_stream(enriched, question)

        full_answer = ""
        for item in token_gen:
            if item["type"] == "token":
                full_answer += item["content"]
            yield item

        self.messages.append({"role": "user", "content": question})
        self.messages.append({"role": "assistant", "content": full_answer})

    def _compute_answer_stream(
        self, enriched: str, question: str
    ) -> Generator[dict, None, None]:
        if self.pandasai is not None:
            try:
                answer = self.pandasai.chat(enriched)
                answer_str = str(answer)
                if not answer_str or answer_str.strip() in ("", "None"):
                    raise ValueError("Empty response from PandasAI")
                yield {"type": "token", "content": answer_str}
            except Exception as e:
                yield from self._langchain_stream(question, str(e))
        else:
            yield from self._langchain_stream(question, "")

    def _langchain_stream(
        self, question: str, error: str = ""
    ) -> Generator[dict, None, None]:
        llm = self._get_llm()
        if llm is None:
            yield {"type": "token", "content": self._local_fallback(question)}
            return

        context = self._build_context()
        system_prompt = (
            f"You are RevenueAI, an AI business analyst. "
            f"You are analyzing a dataset.\n\n{context}\n\n"
            f"Note: The automated data analysis tool encountered an issue "
            f"({error}). Answer based on the available metrics and context."
        )

        try:
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        except ImportError:
            yield {"type": "token", "content": self._local_fallback(question)}
            return

        lc_messages = [SystemMessage(content=system_prompt)]
        for m in self.messages[-6:]:
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

        if "column" in q or "schema" in q or "structure" in q:
            lines = [f"The dataset has {len(self.df.columns)} columns:"]
            for c in cols:
                role = c.get("detected_role", "unknown")
                lines.append(f"  - {c['name']} ({c['dtype']}) -> {role}")
            return "\n".join(lines)

        if ("compare" in q or "category" in q or "breakdown" in q) and revenue_cols and category_cols:
            grouped = self.df.groupby(category_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
            total = float(grouped.sum())
            lines = [f"**Revenue by {category_cols[0].title()}:**"]
            for cat, rev in grouped.items():
                pct = (rev / total * 100) if total else 0
                lines.append(f"  {cat}: ${rev:,.2f} ({pct:.1f}%)")
            return "\n".join(lines)

        if ("top" in q or "best" in q or "ranking" in q or "leading" in q) and revenue_cols and product_cols:
            grouped = self.df.groupby(product_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
            lines = ["**Top Products by Revenue:**"]
            for i, (prod, rev) in enumerate(grouped.head(10).items(), 1):
                lines.append(f"  {i}. {prod} — ${rev:,.2f}")
            return "\n".join(lines)

        if "product" in q and revenue_cols and product_cols:
            keywords = q.split()
            for prod in self.df[product_cols[0]].unique():
                if str(prod).lower() in q:
                    rev = float(self.df[self.df[product_cols[0]] == prod][revenue_cols[0]].sum())
                    return f"**{prod}** generated **${rev:,.2f}** in total revenue."
            grouped = self.df.groupby(product_cols[0])[revenue_cols[0]].sum().sort_values(ascending=False)
            lines = ["**Products by Revenue:**"]
            for prod, rev in grouped.items():
                lines.append(f"  {prod}: ${rev:,.2f}")
            return "\n".join(lines)

        if ("month" in q or "trend" in q or "growth" in q or "monthly" in q or "over time" in q) and revenue_cols and date_cols:
            df = self.df.copy()
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
            df["_month"] = df[date_cols[0]].dt.to_period("M").astype(str)
            monthly = df.groupby("_month")[revenue_cols[0]].sum()
            lines = ["**Monthly Revenue:**"]
            for month, rev in monthly.items():
                lines.append(f"  {month}: ${rev:,.2f}")
            return "\n".join(lines)

        if "growth" in q and revenue_cols and date_cols:
            df = self.df.copy()
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
            df["_month"] = df[date_cols[0]].dt.to_period("M").astype(str)
            monthly = df.groupby("_month")[revenue_cols[0]].sum().sort_index()
            if len(monthly) >= 2:
                growths = monthly.pct_change() * 100
                lines = ["**Month-over-Month Growth:**"]
                for month, g in growths.items():
                    if pd.notna(g):
                        arrow = "▲" if g >= 0 else "▼"
                        lines.append(f"  {month}: {arrow} {g:+.1f}%")
                return "\n".join(lines)

        if ("revenue" in q or "sales" in q or "total" in q or "earnings" in q or "income" in q):
            if revenue_cols:
                total = float(self.df[revenue_cols[0]].sum())
                return f"Based on the data, the total revenue from '{revenue_cols[0]}' is **${total:,.2f}**."
            return f"I found the dataset but couldn't identify a revenue column. Available columns: {list(self.df.columns)}"

        return (
            "I analyzed your dataset. I can answer questions about "
            "revenue, products, trends, and other business metrics. "
            "What would you like to know?"
        )

    def get_messages(self) -> list[dict]:
        if self.pandasai is not None:
            try:
                mem = self.pandasai.context.memory
                return [
                    {
                        "role": "user" if m["is_user"] else "assistant",
                        "content": m["message"],
                    }
                    for m in mem.all()
                ]
            except Exception:
                pass
        return self.messages

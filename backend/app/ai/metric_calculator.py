import pandas as pd
import numpy as np


def _get_role_cols(df: pd.DataFrame, columns_meta: list[dict], role: str) -> list[str]:
    return [m["name"] for m in columns_meta if m["detected_role"] == role]


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _normalized_groups(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Group value_col by group_col with case/whitespace-insensitive keys.

    Messy data often mixes 'Keyboard'/'KEYBOARD' or 'Lagos'/'lagos', which
    would otherwise be counted as separate groups.
    """
    clean = df[[group_col, value_col]].copy()
    clean[group_col] = clean[group_col].astype(str).str.strip()
    clean = clean[
        clean[group_col].notna()
        & (clean[group_col] != "")
        & (~clean[group_col].str.lower().isin(["nan", "none", "null"]))
    ]
    clean["_group_key"] = clean[group_col].str.lower()
    clean[value_col] = pd.to_numeric(clean[value_col], errors="coerce").fillna(0)

    grouped = (
        clean.groupby("_group_key")
        .agg(
            _label=(group_col, lambda s: s.value_counts().index[0].title()),
            _value=(value_col, "sum"),
        )
        .reset_index(drop=True)
    )
    return grouped.sort_values("_value", ascending=False)


def calculate_total_revenue(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    if not revenue_cols:
        return []

    metrics = []
    for col in revenue_cols:
        total = float(_safe_numeric(df[col]).sum())
        metrics.append({
            "metric_type": "total_revenue",
            "metric_name": f"Total {col}",
            "value": round(total, 2),
            "currency": "USD",
            "period": "all",
            "metadata": {"column": col},
            "rank": 1,
        })
    return metrics


def calculate_monthly_revenue(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    date_cols = _get_role_cols(df, columns_meta, "date")

    if not revenue_cols or not date_cols:
        return []

    metrics = []
    revenue_col = revenue_cols[0]
    date_col = date_cols[0]

    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")
        df_copy["_month"] = df_copy[date_col].dt.to_period("M").astype(str)

        monthly = df_copy.groupby("_month")[revenue_col].sum().reset_index()
        monthly[revenue_col] = _safe_numeric(monthly[revenue_col])

        for _, row in monthly.iterrows():
            metrics.append({
                "metric_type": "monthly_revenue",
                "metric_name": f"Revenue {row['_month']}",
                "value": round(float(row[revenue_col]), 2),
                "currency": "USD",
                "period": str(row["_month"]),
                "metadata": {"column": revenue_col},
                "rank": 0,
            })
    except Exception:
        pass

    return metrics


def calculate_growth_rate(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    date_cols = _get_role_cols(df, columns_meta, "date")

    if not revenue_cols or not date_cols:
        return []

    metrics = []
    revenue_col = revenue_cols[0]
    date_col = date_cols[0]

    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")
        df_copy["_month"] = df_copy[date_col].dt.to_period("M").astype(str)

        monthly = df_copy.groupby("_month")[revenue_col].sum().reset_index()
        monthly[revenue_col] = _safe_numeric(monthly[revenue_col])
        monthly = monthly.sort_values("_month")

        if len(monthly) >= 2:
            monthly["_growth"] = monthly[revenue_col].pct_change() * 100
            for _, row in monthly.iterrows():
                if pd.notna(row.get("_growth")):
                    metrics.append({
                        "metric_type": "growth_rate",
                        "metric_name": f"Growth {row['_month']}",
                        "value": round(float(row["_growth"]), 2),
                        "period": str(row["_month"]),
                        "metadata": {"column": revenue_col},
                        "rank": 0,
                    })

            total_growth = ((monthly[revenue_col].iloc[-1] - monthly[revenue_col].iloc[0])
                            / monthly[revenue_col].iloc[0]) * 100
            metrics.append({
                "metric_type": "growth_rate",
                "metric_name": "Overall Growth Rate",
                "value": round(float(total_growth), 2),
                "period": "all",
                "metadata": {"column": revenue_col},
                "rank": 1,
            })
    except Exception:
        pass

    return metrics


def calculate_aov(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    qty_cols = _get_role_cols(df, columns_meta, "quantity")

    if not revenue_cols:
        return []

    revenue_col = revenue_cols[0]
    revenue_series = _safe_numeric(df[revenue_col])

    if qty_cols:
        qty_series = _safe_numeric(df[qty_cols[0]])
        order_count = float(qty_series.sum())
    else:
        order_count = float(len(df))

    total_rev = float(revenue_series.sum())

    aov = round(total_rev / order_count, 2) if order_count > 0 else 0

    return [{
        "metric_type": "aov",
        "metric_name": "Average Order Value",
        "value": aov,
        "currency": "USD",
        "period": "all",
        "metadata": {"total_revenue": total_rev, "order_count": order_count},
        "rank": 1,
    }]


def calculate_top_products(df: pd.DataFrame, columns_meta: list[dict], top_n: int = 10) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    product_cols = _get_role_cols(df, columns_meta, "product")

    if not revenue_cols or not product_cols:
        return []

    revenue_col = revenue_cols[0]
    product_col = product_cols[0]

    metrics = []
    try:
        grouped = _normalized_groups(df, product_col, revenue_col).head(top_n)

        for rank, (_, row) in enumerate(grouped.iterrows(), 1):
            metrics.append({
                "metric_type": "top_products",
                "metric_name": str(row["_label"]),
                "value": round(float(row["_value"]), 2),
                "currency": "USD",
                "period": "all",
                "metadata": {"column": revenue_col, "product_column": product_col},
                "rank": rank,
            })
    except Exception:
        pass

    return metrics


def calculate_category_breakdown(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    category_cols = _get_role_cols(df, columns_meta, "category")

    if not revenue_cols or not category_cols:
        return []

    revenue_col = revenue_cols[0]
    category_col = category_cols[0]

    metrics = []
    try:
        grouped = _normalized_groups(df, category_col, revenue_col)

        total = float(grouped["_value"].sum())

        for rank, (_, row) in enumerate(grouped.iterrows(), 1):
            val = float(row["_value"])
            pct = round((val / total * 100), 2) if total > 0 else 0
            metrics.append({
                "metric_type": "category_breakdown",
                "metric_name": str(row["_label"]),
                "value": round(val, 2),
                "currency": "USD",
                "period": "all",
                "metadata": {
                    "column": revenue_col,
                    "category_column": category_col,
                    "percentage": pct,
                },
                "rank": rank,
            })
    except Exception:
        pass

    return metrics


def calculate_trends(df: pd.DataFrame, columns_meta: list[dict]) -> list[dict]:
    revenue_cols = _get_role_cols(df, columns_meta, "revenue")
    date_cols = _get_role_cols(df, columns_meta, "date")

    if not revenue_cols or not date_cols:
        return []

    metrics = []
    revenue_col = revenue_cols[0]
    date_col = date_cols[0]

    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")
        df_copy["_month"] = df_copy[date_col].dt.to_period("M").astype(str)

        monthly = df_copy.groupby("_month")[revenue_col].sum().reset_index()
        monthly[revenue_col] = _safe_numeric(monthly[revenue_col])
        monthly = monthly.sort_values("_month")

        if len(monthly) >= 3:
            monthly["_rolling_avg"] = monthly[revenue_col].rolling(window=3, min_periods=1).mean()
            for _, row in monthly.iterrows():
                metrics.append({
                    "metric_type": "trends",
                    "metric_name": f"3-Month Avg {row['_month']}",
                    "value": round(float(row["_rolling_avg"]), 2),
                    "currency": "USD",
                    "period": str(row["_month"]),
                    "metadata": {"type": "rolling_average", "column": revenue_col},
                    "rank": 0,
                })

            mean_val = float(monthly[revenue_col].mean())
            std_val = float(monthly[revenue_col].std())
            for _, row in monthly.iterrows():
                val = float(row[revenue_col])
                if std_val > 0:
                    z_score = (val - mean_val) / std_val
                    if abs(z_score) > 1.5:
                        metrics.append({
                            "metric_type": "trends",
                            "metric_name": f"Anomaly {row['_month']}",
                            "value": round(val, 2),
                            "currency": "USD",
                            "period": str(row["_month"]),
                            "metadata": {
                                "type": "anomaly",
                                "z_score": round(z_score, 2),
                                "column": revenue_col,
                            },
                            "rank": 0,
                        })
    except Exception:
        pass

    return metrics


def calculate_all_metrics(df: pd.DataFrame, columns_meta: list[dict]) -> dict:
    return {
        "total_revenue": calculate_total_revenue(df, columns_meta),
        "monthly_revenue": calculate_monthly_revenue(df, columns_meta),
        "growth_rate": calculate_growth_rate(df, columns_meta),
        "aov": calculate_aov(df, columns_meta),
        "top_products": calculate_top_products(df, columns_meta),
        "category_breakdown": calculate_category_breakdown(df, columns_meta),
        "trends": calculate_trends(df, columns_meta),
    }

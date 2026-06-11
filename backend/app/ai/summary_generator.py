"""Builds a plain-language executive summary for a dataset.

Computed live from the dataframe so it works for every dataset,
including ones uploaded before this feature existed.
"""

import pandas as pd

from app.ai.metric_calculator import _normalized_groups, _safe_numeric


LOCATION_HINTS = ["state", "region", "country", "city", "location", "province", "area"]


def _role_cols(columns_meta: list[dict], role: str) -> list[str]:
    return [m["name"] for m in columns_meta if m.get("detected_role") == role]


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _ranked(df: pd.DataFrame, group_col: str, revenue_col: str) -> list[dict]:
    grouped = _normalized_groups(df, group_col, revenue_col)
    return [
        {"name": str(row["_label"]), "value": round(float(row["_value"]), 2)}
        for _, row in grouped.iterrows()
    ]


def _case_variants(df: pd.DataFrame, col: str) -> list[str]:
    """Find values that appear with inconsistent capitalization, e.g. Keyboard/KEYBOARD."""
    values = df[col].dropna().astype(str).str.strip()
    values = values[values != ""]
    variants = values.groupby(values.str.lower()).nunique()
    messy_keys = variants[variants > 1].index.tolist()

    examples = []
    for key in messy_keys[:5]:
        forms = sorted(values[values.str.lower() == key].unique())[:3]
        examples.append(" / ".join(forms))
    return examples


def generate_summary(df: pd.DataFrame, columns_meta: list[dict], dataset_name: str) -> dict:
    revenue_cols = _role_cols(columns_meta, "revenue")
    product_cols = _role_cols(columns_meta, "product")
    customer_cols = _role_cols(columns_meta, "customer")
    category_cols = _role_cols(columns_meta, "category")
    date_cols = _role_cols(columns_meta, "date")

    overview: list[str] = []
    advice: list[str] = []
    data_quality: list[str] = []

    summary: dict = {
        "overview": overview,
        "top_products": [],
        "low_products": [],
        "top_customers": [],
        "top_regions": [],
        "low_regions": [],
        "region_column": None,
        "advice": advice,
        "data_quality": data_quality,
    }

    overview.append(
        f"This report analyzes '{dataset_name}' with {len(df):,} rows and {len(df.columns)} columns."
    )

    if not revenue_cols:
        overview.append(
            "No revenue column was detected, so financial analysis is limited. "
            "Make sure your file has a column like 'Revenue', 'Sales' or 'Amount'."
        )
        return summary

    revenue_col = revenue_cols[0]
    total_revenue = float(_safe_numeric(df[revenue_col]).sum())
    overview.append(f"Total revenue across the dataset is {_money(total_revenue)}.")

    # --- Products: best and worst sellers ---
    if product_cols:
        products = _ranked(df, product_cols[0], revenue_col)
        summary["top_products"] = products[:3]
        # Bottom performers, excluding anything already shown in the top list.
        remainder = products[3:]
        summary["low_products"] = list(reversed(remainder[-3:]))

        if products:
            top = products[0]
            share = (top["value"] / total_revenue * 100) if total_revenue > 0 else 0
            overview.append(
                f"The top product is '{top['name']}' with {_money(top['value'])} "
                f"({share:.1f}% of total revenue)."
            )
            advice.append(
                f"'{top['name']}' is your best seller — make sure it stays in stock and "
                f"consider featuring it in marketing campaigns."
            )
            if share > 30:
                advice.append(
                    f"'{top['name']}' alone makes up {share:.1f}% of revenue. Relying heavily on "
                    f"one product is risky — consider promoting other products to diversify."
                )
        if summary["low_products"]:
            worst = summary["low_products"][0]
            overview.append(
                f"The weakest product is '{worst['name']}' with only {_money(worst['value'])} in sales."
            )
            advice.append(
                f"'{worst['name']}' sells the least. Consider running a promotion, bundling it "
                f"with popular products, or discontinuing it if margins are poor."
            )

    # --- Customers: top 3 ---
    if customer_cols:
        customers = _ranked(df, customer_cols[0], revenue_col)
        summary["top_customers"] = customers[:3]
        if customers:
            names = ", ".join(f"'{c['name']}'" for c in customers[:3])
            overview.append(f"Your top customers by revenue are {names}.")
            advice.append(
                "Your top 3 customers generate significant revenue — keep them loyal with "
                "personal follow-ups, loyalty rewards, or exclusive offers."
            )

    # --- Regions / states: prefer a location-like category column ---
    if category_cols:
        region_col = next(
            (c for c in category_cols if any(h in c.lower() for h in LOCATION_HINTS)),
            category_cols[0],
        )
        summary["region_column"] = region_col
        regions = _ranked(df, region_col, revenue_col)
        summary["top_regions"] = regions[:3]
        remainder = regions[3:]
        summary["low_regions"] = list(reversed(remainder[-3:]))

        if regions:
            best = regions[0]
            overview.append(
                f"By {region_col}, '{best['name']}' leads with {_money(best['value'])}."
            )
        if summary["low_regions"]:
            weakest = summary["low_regions"][0]
            advice.append(
                f"'{weakest['name']}' is the weakest {region_col} ({_money(weakest['value'])}). "
                f"Investigate whether this is a distribution, pricing, or awareness problem "
                f"before investing more there."
            )

    # --- Time: best and worst month ---
    if date_cols:
        try:
            tmp = df[[date_cols[0], revenue_col]].copy()
            tmp[date_cols[0]] = pd.to_datetime(tmp[date_cols[0]], errors="coerce")
            tmp[revenue_col] = _safe_numeric(tmp[revenue_col])
            tmp = tmp.dropna(subset=[date_cols[0]])
            monthly = tmp.groupby(tmp[date_cols[0]].dt.to_period("M"))[revenue_col].sum()
            if len(monthly) >= 2:
                best_m, worst_m = monthly.idxmax(), monthly.idxmin()
                overview.append(
                    f"The strongest month was {best_m} ({_money(float(monthly.max()))}) and the "
                    f"weakest was {worst_m} ({_money(float(monthly.min()))})."
                )
                advice.append(
                    f"Sales dipped in {worst_m}. Plan promotions or campaigns ahead of "
                    f"historically slow months to smooth out revenue."
                )
        except Exception:
            pass

    # --- Data quality warnings ---
    for col in (product_cols + category_cols + customer_cols)[:5]:
        examples = _case_variants(df, col)
        if examples:
            data_quality.append(
                f"Column '{col}' has inconsistent capitalization (e.g. {examples[0]}). "
                f"These were merged automatically in this analysis, but cleaning the source "
                f"data is recommended."
            )

    missing = df.isna().sum()
    for col, count in missing[missing > 0].items():
        pct = count / len(df) * 100
        if pct >= 5:
            data_quality.append(
                f"Column '{col}' is missing {int(count)} values ({pct:.0f}% of rows), "
                f"which may make results less accurate."
            )

    if data_quality:
        advice.append(
            "Improve your data quality: fix inconsistent spellings/capitalization and fill in "
            "missing values so future analyses are more reliable."
        )

    return summary

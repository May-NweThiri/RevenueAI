"""RevenueAI evaluation harness.

Measures the technical accuracy of the analysis pipeline:

  1. CSV parsing            — do generated files load without errors?
  2. Column detection       — detected roles vs known ground truth
  3. Metric correctness     — app-computed metrics vs independently
                              computed ground truth (plain Python, no pandas)

It also exports the test CSVs plus a chat answer key, so you can upload the
same files in the web app and manually score the AI chat's answers.

Usage (from the backend/ directory):

    .venv/bin/python tests/evaluation/run_evaluation.py
"""

import io
import os
import random
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

# Force offline mode so column detection never calls the Gemini/OpenAI API:
# results must be deterministic and free to compute.
os.environ["GEMINI_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from app.utils.file_parser import parse_file  # noqa: E402
from app.ai.column_detector import detect_columns  # noqa: E402
from app.ai.metric_calculator import calculate_all_metrics  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "data"
TOLERANCE = 0.01

PRODUCT_PRICES = {
    "Phone": 450.0,
    "Laptop": 1200.0,
    "Keyboard": 35.0,
    "Monitor": 220.0,
    "Tablet": 310.0,
}
PRODUCT_CATEGORY = {
    "Phone": "Electronics",
    "Laptop": "Computers",
    "Keyboard": "Accessories",
    "Monitor": "Computers",
    "Tablet": "Electronics",
}
STATES = ["Lagos", "Kano", "Rivers", "Abuja", "Oyo"]
CUSTOMERS = ["Acme Corp", "Globex Ltd", "Initech", "Umbrella Inc", "Stark Industries"]
CHANNELS = ["Online", "Retail", "Wholesale"]


# ---------------------------------------------------------------------------
# Test data generation (deterministic, seeded)
# ---------------------------------------------------------------------------

def _random_date(rng: random.Random) -> str:
    start = date(2024, 1, 1)
    span = (date(2025, 6, 30) - start).days
    return (start + timedelta(days=rng.randint(0, span))).isoformat()


def _generate_rows(rng: random.Random, n: int) -> list[dict]:
    rows = []
    for _ in range(n):
        product = rng.choice(list(PRODUCT_PRICES))
        qty = rng.randint(1, 5)
        unit_price = round(PRODUCT_PRICES[product] * rng.uniform(0.9, 1.1), 2)
        rows.append({
            "order_date": _random_date(rng),
            "customer": rng.choice(CUSTOMERS),
            "product": product,
            "category": PRODUCT_CATEGORY[product],
            "state": rng.choice(STATES),
            "channel": rng.choice(CHANNELS),
            "quantity": qty,
            "unit_price": unit_price,
            "revenue": round(qty * unit_price, 2),
        })
    return rows


def _mangle_case(rng: random.Random, value: str) -> str:
    roll = rng.random()
    if roll < 0.2:
        return value.upper()
    if roll < 0.3:
        return value.lower()
    if roll < 0.4:
        return f"  {value} "
    return value


def make_clean_dataset() -> tuple[str, list[dict], dict]:
    rng = random.Random(42)
    rows = _generate_rows(rng, 400)
    header = [
        "Order ID", "Order Date", "Customer Name", "Product", "Category",
        "State", "Quantity", "Unit Price", "Revenue",
    ]
    csv_rows = [
        [
            f"ORD-{i:04d}", r["order_date"], r["customer"], r["product"],
            r["category"], r["state"], r["quantity"], r["unit_price"], r["revenue"],
        ]
        for i, r in enumerate(rows, 1)
    ]
    expected_roles = {
        "Order ID": "id", "Order Date": "date", "Customer Name": "customer",
        "Product": "product", "Category": "category", "State": "category",
        "Quantity": "quantity", "Unit Price": "unit_price", "Revenue": "revenue",
    }
    return _to_csv(header, csv_rows), rows, expected_roles


def make_messy_dataset() -> tuple[str, list[dict], dict]:
    rng = random.Random(7)
    rows = _generate_rows(rng, 400)
    for r in rows:
        r["product_raw"] = _mangle_case(rng, r["product"])
        r["state_raw"] = _mangle_case(rng, r["state"])
        r["customer_raw"] = _mangle_case(rng, r["customer"])
        if rng.random() < 0.05:
            r["revenue"] = None  # missing value -> app treats as 0
    header = [
        "Order ID", "Order Date", "Customer Name", "Product", "Category",
        "State", "Quantity", "Unit Price", "Revenue",
    ]
    csv_rows = [
        [
            f"ORD-{i:04d}", r["order_date"], r["customer_raw"], r["product_raw"],
            r["category"], r["state_raw"], r["quantity"], r["unit_price"],
            "" if r["revenue"] is None else r["revenue"],
        ]
        for i, r in enumerate(rows, 1)
    ]
    expected_roles = {
        "Order ID": "id", "Order Date": "date", "Customer Name": "customer",
        "Product": "product", "Category": "category", "State": "category",
        "Quantity": "quantity", "Unit Price": "unit_price", "Revenue": "revenue",
    }
    return _to_csv(header, csv_rows), rows, expected_roles


def make_alt_names_dataset() -> tuple[str, list[dict], dict]:
    rng = random.Random(99)
    rows = _generate_rows(rng, 300)
    header = [
        "Transaction ID", "Transaction Date", "Client", "Item", "Sales Channel",
        "Region", "Units", "Rate", "Sales Amount",
    ]
    csv_rows = [
        [
            f"TX-{i:05d}", r["order_date"], r["customer"], r["product"],
            r["channel"], r["state"], r["quantity"], r["unit_price"], r["revenue"],
        ]
        for i, r in enumerate(rows, 1)
    ]
    expected_roles = {
        "Transaction ID": "id", "Transaction Date": "date", "Client": "customer",
        "Item": "product", "Sales Channel": "category", "Region": "category",
        "Units": "quantity", "Rate": "unit_price", "Sales Amount": "revenue",
    }
    return _to_csv(header, csv_rows), rows, expected_roles


def _to_csv(header: list[str], rows: list[list]) -> str:
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(str(v) for v in row))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Independent ground truth (plain Python — no pandas, no app code)
# ---------------------------------------------------------------------------

def compute_ground_truth(rows: list[dict], group_field_map: dict) -> dict:
    """group_field_map maps logical names -> row field, e.g. {'category': 'channel'}."""
    total = 0.0
    qty_total = 0
    by_month: dict[str, float] = defaultdict(float)
    by_product: dict[str, float] = defaultdict(float)
    by_category: dict[str, float] = defaultdict(float)

    cat_field = group_field_map.get("category", "category")
    for r in rows:
        rev = r["revenue"] if r["revenue"] is not None else 0.0
        total += rev
        qty_total += r["quantity"]
        by_month[r["order_date"][:7]] += rev
        by_product[r["product"].strip().lower()] += rev
        by_category[str(r[cat_field]).strip().lower()] += rev

    months = sorted(by_month)
    first, last = by_month[months[0]], by_month[months[-1]]
    growth = ((last - first) / first * 100) if first else None

    return {
        "total_revenue": total,
        "monthly_revenue": dict(by_month),
        "by_product": dict(by_product),
        "by_category": dict(by_category),
        "aov": total / qty_total if qty_total else 0.0,
        "overall_growth": growth,
    }


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def close(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= TOLERANCE


def check_metrics(metrics: dict, truth: dict) -> list[tuple[str, bool, str]]:
    results = []

    # Total revenue
    app_total = metrics["total_revenue"][0]["value"] if metrics["total_revenue"] else None
    ok = app_total is not None and close(app_total, truth["total_revenue"])
    results.append(("Total revenue", ok,
                    f"app={app_total} expected={truth['total_revenue']:.2f}"))

    # Monthly revenue: every month must be present and match
    app_monthly = {m["period"]: m["value"] for m in metrics["monthly_revenue"]}
    missing = [m for m in truth["monthly_revenue"] if m not in app_monthly]
    wrong = [
        m for m, v in truth["monthly_revenue"].items()
        if m in app_monthly and not close(app_monthly[m], v)
    ]
    ok = not missing and not wrong and len(app_monthly) == len(truth["monthly_revenue"])
    detail = f"{len(app_monthly)}/{len(truth['monthly_revenue'])} months"
    if missing:
        detail += f", missing={missing[:3]}"
    if wrong:
        detail += f", wrong={wrong[:3]}"
    results.append(("Monthly revenue (all months)", ok, detail))

    # Overall growth rate
    app_growth = next(
        (m["value"] for m in metrics["growth_rate"] if m["period"] == "all"), None
    )
    ok = (
        app_growth is not None
        and truth["overall_growth"] is not None
        and close(app_growth, round(truth["overall_growth"], 2))
    )
    results.append(("Overall growth rate", ok,
                    f"app={app_growth} expected={truth['overall_growth']:.2f}"))

    # AOV
    app_aov = metrics["aov"][0]["value"] if metrics["aov"] else None
    ok = app_aov is not None and close(app_aov, round(truth["aov"], 2))
    results.append(("Average order value", ok,
                    f"app={app_aov} expected={truth['aov']:.2f}"))

    # Top products: names (case-insensitive) and values must match, no duplicates
    app_products = {
        m["metric_name"].strip().lower(): m["value"] for m in metrics["top_products"]
    }
    dup = len(app_products) != len(metrics["top_products"])
    wrong = [
        name for name, v in truth["by_product"].items()
        if name not in app_products or not close(app_products[name], round(v, 2))
    ]
    ok = not dup and not wrong and len(app_products) == len(truth["by_product"])
    detail = f"{len(app_products)} products"
    if dup:
        detail += ", case-duplicates found"
    if wrong:
        detail += f", mismatched={wrong[:3]}"
    results.append(("Top products (case-merged)", ok, detail))

    # Category breakdown
    app_cats = {
        m["metric_name"].strip().lower(): m["value"]
        for m in metrics["category_breakdown"]
    }
    wrong = [
        name for name, v in truth["by_category"].items()
        if name not in app_cats or not close(app_cats[name], round(v, 2))
    ]
    ok = not wrong and len(app_cats) == len(truth["by_category"])
    results.append(("Category breakdown", ok,
                    f"{len(app_cats)}/{len(truth['by_category'])} categories"
                    + (f", mismatched={wrong[:3]}" if wrong else "")))

    return results


def check_columns(columns_meta: list[dict], expected: dict) -> tuple[int, int, list[str]]:
    correct = 0
    mistakes = []
    for meta in columns_meta:
        want = expected.get(meta["name"])
        got = meta["detected_role"]
        if want is None:
            continue
        if got == want:
            correct += 1
        else:
            mistakes.append(f"{meta['name']}: expected '{want}', got '{got}'")
    return correct, len(expected), mistakes


# ---------------------------------------------------------------------------
# Chat answer key (for manual AI-chat scoring)
# ---------------------------------------------------------------------------

def write_answer_key(name: str, truth: dict, fh) -> None:
    fh.write(f"\n## {name}\n\n")
    fh.write(f"- **Total revenue:** ${truth['total_revenue']:,.2f}\n")
    fh.write(f"- **Average order value:** ${truth['aov']:,.2f}\n")
    if truth["overall_growth"] is not None:
        fh.write(f"- **Overall growth rate:** {truth['overall_growth']:+.2f}%\n")

    top = sorted(truth["by_product"].items(), key=lambda kv: kv[1], reverse=True)
    fh.write("- **Top 3 products:** "
             + ", ".join(f"{n.title()} (${v:,.2f})" for n, v in top[:3]) + "\n")
    fh.write(f"- **Weakest product:** {top[-1][0].title()} (${top[-1][1]:,.2f})\n")

    months = sorted(truth["monthly_revenue"].items())
    best = max(months, key=lambda kv: kv[1])
    worst = min(months, key=lambda kv: kv[1])
    fh.write(f"- **Best month:** {best[0]} (${best[1]:,.2f})\n")
    fh.write(f"- **Worst month:** {worst[0]} (${worst[1]:,.2f})\n")
    fh.write("\n**Monthly revenue:**\n\n")
    for month, val in months:
        fh.write(f"| {month} | ${val:,.2f} |\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "clean_sales": make_clean_dataset(),
        "messy_sales": make_messy_dataset(),
        "alt_names_sales": make_alt_names_dataset(),
    }

    total_cols = correct_cols = 0
    total_checks = passed_checks = 0
    parse_ok = 0

    answer_key_path = DATA_DIR / "chat_answer_key.md"
    key_fh = open(answer_key_path, "w")
    key_fh.write("# RevenueAI chat answer key\n\n"
                 "Upload the CSVs in this folder, ask the AI chat the questions "
                 "below, and compare its answers with these ground-truth values.\n")

    print("=" * 70)
    print("RevenueAI Evaluation Report")
    print("=" * 70)

    for name, (csv_text, rows, expected_roles) in datasets.items():
        csv_path = DATA_DIR / f"{name}.csv"
        csv_path.write_text(csv_text)

        cat_field = "channel" if name == "alt_names_sales" else "category"
        truth = compute_ground_truth(rows, {"category": cat_field})
        write_answer_key(name, truth, key_fh)

        print(f"\n--- Dataset: {name} ({len(rows)} rows) ---")

        # 1. Parsing through the real ingestion path
        try:
            df = parse_file(io.BytesIO(csv_text.encode("utf-8")), file_ext=".csv")
            parse_ok += 1
            print(f"  [PASS] CSV parsing ({len(df)} rows, {len(df.columns)} cols)")
        except Exception as e:
            print(f"  [FAIL] CSV parsing: {e}")
            continue

        # 2. Column detection
        columns_meta = detect_columns(df)
        correct, total, mistakes = check_columns(columns_meta, expected_roles)
        correct_cols += correct
        total_cols += total
        status = "PASS" if correct == total else "WARN"
        print(f"  [{status}] Column detection: {correct}/{total} correct")
        for m in mistakes:
            print(f"         - {m}")

        # 3. Metric correctness
        metrics = calculate_all_metrics(df, columns_meta)
        for check_name, ok, detail in check_metrics(metrics, truth):
            total_checks += 1
            passed_checks += ok
            print(f"  [{'PASS' if ok else 'FAIL'}] {check_name}: {detail}")

    key_fh.close()

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    col_acc = correct_cols / total_cols * 100 if total_cols else 0
    metric_acc = passed_checks / total_checks * 100 if total_checks else 0
    print(f"  CSV parsing success:        {parse_ok}/{len(datasets)}")
    print(f"  Column detection accuracy:  {col_acc:.1f}%  ({correct_cols}/{total_cols})")
    print(f"  Metric exact-match rate:    {metric_acc:.1f}%  ({passed_checks}/{total_checks})")
    print(f"\n  Test CSVs + chat answer key written to:\n  {DATA_DIR}")
    print("  Upload these CSVs in the web app to score the AI chat manually.")

    return 0 if (parse_ok == len(datasets) and passed_checks == total_checks) else 1


if __name__ == "__main__":
    sys.exit(main())

# FinX AI
https://finx-ai-app-delta.vercel.app/

AI-powered revenue analytics platform. Upload a sales CSV/Excel file and get an automatic dashboard with KPIs, charts, a plain-language executive summary with recommendations, data-quality warnings, an AI chat to ask questions about your data, and a downloadable PDF report.

**Live demo**

| Part | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://revenue-ai-delta.vercel.app |
| Backend API | Railway | https://revenueai-production.up.railway.app |
| Health check | — | https://revenueai-production.up.railway.app/health |

---

## 1. Architecture

```
┌──────────────┐     HTTPS / REST      ┌───────────────┐
│   Frontend   │ ───────────────────►  │    Backend    │
│  Next.js 14  │                       │    FastAPI    │
│   (Vercel)   │ ◄───────────────────  │   (Railway)   │
└──────────────┘     JSON responses    └───────┬───────┘
                                               │
                          ┌────────────────────┼─────────────────────┐
                          ▼                    ▼                     ▼
                  ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
                  │   Supabase   │    │    Supabase    │    │  Gemini API  │
                  │  PostgreSQL  │    │     Storage    │    │  (free tier) │
                  │  (metadata,  │    │  (uploaded CSV │    │  AI chat +   │
                  │   metrics)   │    │   /xlsx files) │    │   insights   │
                  └──────────────┘    └────────────────┘    └──────────────┘
```

### Data flow (upload → dashboard)

1. **Upload** — user uploads CSV/XLSX → stored in Supabase Storage
2. **Parse** — `file_parser.py` auto-detects encoding (UTF-8/Latin-1/CP1252) and separator (comma/semicolon/tab)
3. **Column detection** — `column_detector.py` assigns a role to each column (revenue, product, customer, date, category, quantity, ...) using keyword heuristics + numeric-type guards, optionally confirmed by the AI
4. **Metrics** — `metric_calculator.py` computes total revenue, monthly revenue, growth rate, AOV, top products, category breakdown, anomalies — with case/whitespace-insensitive grouping so `Keyboard`/`KEYBOARD`/` keyboard ` merge into one
5. **Insights** — `insight_engine.py` generates AI insights (falls back to rule-based templates without an API key)
6. **Dashboard** — frontend renders KPI cards, Recharts graphs, executive summary, recommendations, and data-quality warnings
7. **AI Chat** — `chat_agent.py` answers questions with full computed aggregates (every month, all products/categories) in its context
8. **PDF export** — `html2canvas` + `jsPDF` snapshot the report client-side

### Tech stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, html2canvas, jsPDF
- **Backend:** FastAPI, SQLAlchemy, Pandas/NumPy, OpenAI SDK (works with both OpenAI and Gemini via Google's OpenAI-compatible endpoint)
- **Infra:** Railway (Docker), Vercel, Supabase (PostgreSQL + Storage)

Full folder structure: see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 2. Project progress

- [x] File upload (CSV/XLSX) with robust parsing of messy real-world files
- [x] Automatic column role detection (handles non-standard names: `Client`, `Item`, `Sales Amount`, `Region`, ...)
- [x] Metric engine: total/monthly revenue, growth, AOV, top products, category breakdown, anomaly detection
- [x] Dashboard with interactive charts (revenue trend, category pie, top products bar, MoM growth)
- [x] Plain-language Executive Summary: top/lowest products, top 3 customers, top states/regions, best/worst month, actionable recommendations, data-quality warnings
- [x] AI chat over the dataset (Gemini free tier or OpenAI), with complete aggregates in context and a no-key fallback mode
- [x] PDF report download (charts + summary)
- [x] Production deployment: Railway + Vercel + Supabase
- [x] Evaluation harness measuring accuracy (see §5)

---

## 3. Deployment errors and how they were fixed

Everything below actually happened during deployment, in roughly chronological order.

| # | Error | Root cause | Fix |
|---|---|---|---|
| 1 | Railway build failed (`pkg_resources`, no wheel for `pandasai` on Python 3.12) | Heavy/AI dependencies incompatible with the build image | Removed `pandasai` (and later all `langchain` packages), upgraded `pandas`, pinned compatible versions |
| 2 | App wouldn't start: `uvicorn: command not found`, `$PORT` not expanded | Railway Nixpacks doesn't expand env vars in `startCommand` | Added `start.sh` wrapper + `python -m uvicorn`, `runtime.txt` for Python 3.12 |
| 3 | Frontend showed `Failed to fetch` on every API error | FastAPI error responses lacked CORS headers, so the browser hid the real error | Custom exception handlers that always attach CORS headers; exact Vercel origin in `CORS_ORIGINS` |
| 4 | `/health` reported `database: unavailable` although `DATABASE_URL` was set | App defaulted to ephemeral SQLite; later, module-level `db_available` flag was imported **by value** so it never updated (stale import bug); a local variable also shadowed the `db` module (`UnboundLocalError`) | Connected Supabase PostgreSQL via the pooler (port 6543, `sslmode=require`, `pool_pre_ping`); read flags via the module (`db.db_available`); renamed the shadowing variable |
| 5 | Chat/preview crashed in production but worked locally | Backend tried to read uploaded files from the local disk path, but files live in private Supabase Storage | New `dataset_file_loader.py` that downloads from Supabase Storage with local-path fallback |
| 6 | Next.js routing broke after adding API rewrites | A catch-all rewrite in `vercel.json` swallowed app routes | Removed the catch-all rewrite |

---

## 4. Bugs found and how they were fixed

| # | Bug | Root cause | Fix |
|---|---|---|---|
| 1 | `Error tokenizing data. C error: Expected 2 fields in line 13, saw 4` on upload | Strict pandas CSV reader; files with odd separators/encodings/unquoted commas failed | Rewrote parser: encoding fallbacks, `csv.Sniffer` separator detection, multiple parse strategies, human-readable error messages |
| 2 | "Top Products" listed **customer names** | `Customer Name` matched the product keyword `name` before customer keywords were checked | Reordered detection: customer keywords checked before product keywords |
| 3 | Text column `Sales Channel` detected as **revenue** | Keyword `sales` matched with no type check | Monetary/quantity roles now require a numeric column (`is_numeric` guard) |
| 4 | `Keyboard` and `KEYBOARD` counted as two different products | Case-sensitive groupby | `_normalized_groups()`: trim + lowercase grouping keys, sum values, display the most common label |
| 5 | AI chat silently returned generic answers despite an API key | Errors were swallowed; the real cause was OpenAI `RateLimitError 429` (no billing) | Direct SDK calls with error surfacing; switched to **Gemini free tier** via Google's OpenAI-compatible endpoint |
| 6 | AI chat said monthly data "not available" when asked for all months | Chat context only contained 3 sample metrics per type | Chat context now includes **complete** computed aggregates (all months, products, categories) recalculated from the full dataframe |
| 7 | Growth Rate KPI showed +46.4% while AI Insights said +3.8% | KPI card picked the first growth metric (last month's MoM) instead of overall growth | KPI uses the `period == "all"` overall growth rate, labeled "first vs last month" |
| 8 | Trend chart appeared to skip month 2025-05 | Recharts hid one crowded X-axis label, looking like missing data | `interval="equidistantPreserveStart"` so labels skip evenly |
| 9 | Same product appeared in both "Top" and "Lowest-Selling" lists | With ≤5 products the bottom-3 overlapped the top-3 | Lowest-selling list excludes anything already in the top 3 |
| 10 | `.env.local` (API keys) at risk of being committed | Missing gitignore entry | Added `.env.local` / `.env*.local` to `.gitignore` |

---

## 5. Accuracy evaluation

A reproducible evaluation harness lives at `backend/tests/evaluation/run_evaluation.py`. It generates three ground-truth datasets and runs the **real** pipeline (parser → column detector → metric calculator), comparing every result against independently computed values (plain Python, no pandas):

- `clean_sales.csv` — 400 rows, well-formatted
- `messy_sales.csv` — 400 rows with case variants (`KEYBOARD`/`keyboard`), extra whitespace, and missing revenue values
- `alt_names_sales.csv` — 300 rows with non-standard column names (`Client`, `Item`, `Rate`, `Sales Amount`, `Region`)

### Results (Jun 11, 2026)

| Component | Metric | Score |
|---|---|---|
| CSV parsing | Success rate | **3/3 (100%)** |
| Column detection | Role accuracy | **27/27 (100%)** |
| Metric calculations | Exact-match rate (total/monthly revenue, growth, AOV, top products, categories) | **18/18 (100%)** |
| Dashboard summary | Manual check vs ground truth, all 3 datasets | **All values correct** |
| Case-variant merging | Messy dataset products/customers/states deduplicated | **Working** |
| Data-quality detection | Messy columns flagged | **3/3 columns** |

Manual end-to-end verification of the deployed app surfaced 3 presentation bugs (rows 7–9 in §4) even though the underlying numbers were correct — all fixed.

### Reproduce it

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tests/evaluation/run_evaluation.py
```

The script also writes `backend/tests/evaluation/data/chat_answer_key.md` — upload the generated CSVs in the web app and compare the AI chat's answers against the key to score chat accuracy manually.

---

## 6. Running locally

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # fill in your values
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev                  # http://localhost:3000
```

### Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | Railway / `.env` | Supabase PostgreSQL pooler URI (port 6543, `sslmode=require`) |
| `STORAGE_BACKEND` | Railway | `supabase` in production, `local` for development |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_STORAGE_BUCKET` | Railway | File storage |
| `GEMINI_API_KEY` | Railway | **Free** AI provider — get a key at https://aistudio.google.com/apikey |
| `OPENAI_API_KEY` | Railway | Optional paid alternative (Gemini wins if both are set) |
| `CORS_ORIGINS` | Railway | Comma-separated allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | Vercel | Backend base URL |

Without any AI key the app still works: insights and chat fall back to rule-based analysis computed with pandas.

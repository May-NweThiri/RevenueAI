# RevenueAI — Architecture Design

---

## 1. Folder Structure (Monorepo)

```
RevenueAI/
├── frontend/                        # Next.js 14 App Router
│   ├── app/
│   │   ├── layout.tsx               # Root layout (ThemeProvider, etc.)
│   │   ├── page.tsx                 # Landing / Marketing page
│   │   ├── dashboard/
│   │   │   ├── page.tsx             # Main dashboard (KPI cards, charts)
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Specific dataset dashboard
│   │   ├── upload/
│   │   │   └── page.tsx             # File upload page
│   │   ├── analytics/
│   │   │   └── [id]/
│   │   │       ├── page.tsx         # Deep analytics view
│   │   │       └── chat/
│   │   │           └── page.tsx     # AI chat for a dataset
│   │   └── settings/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/                      # shadcn/ui primitives
│   │   ├── layout/
│   │   │   ├── sidebar.tsx
│   │   │   ├── navbar.tsx
│   │   │   └── mobile-nav.tsx
│   │   ├── dashboard/
│   │   │   ├── kpi-card.tsx
│   │   │   ├── revenue-chart.tsx
│   │   │   ├── growth-chart.tsx
│   │   │   ├── top-products.tsx
│   │   │   └── metrics-grid.tsx
│   │   ├── charts/
│   │   │   ├── line-chart.tsx
│   │   │   ├── bar-chart.tsx
│   │   │   ├── pie-chart.tsx
│   │   │   └── chart-container.tsx
│   │   ├── chat/
│   │   │   ├── chat-window.tsx
│   │   │   ├── chat-message.tsx
│   │   │   ├── chat-input.tsx
│   │   │   └── insight-card.tsx
│   │   ├── upload/
│   │   │   ├── file-dropzone.tsx
│   │   │   ├── upload-progress.tsx
│   │   │   └── preview-table.tsx
│   │   └── shared/
│   │       ├── glass-card.tsx       # Glassmorphism wrapper
│   │       ├── loading-spinner.tsx
│   │       └── empty-state.tsx
│   ├── lib/
│   │   ├── api-client.ts            # Axios/fetch wrapper
│   │   ├── utils.ts                 # cn(), formatters
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── use-dataset.ts
│   │   ├── use-chat.ts
│   │   ├── use-metrics.ts
│   │   └── use-insights.ts
│   ├── store/
│   │   └── index.ts                 # Zustand store
│   ├── types/
│   │   ├── dataset.ts
│   │   ├── metrics.ts
│   │   ├── chart.ts
│   │   ├── insight.ts
│   │   └── chat.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── backend/                         # FastAPI + Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Settings / env vars
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # Main router aggregator
│   │   │   ├── deps.py              # Dependency injection
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── upload.py
│   │   │   │   ├── datasets.py
│   │   │   │   ├── metrics.py
│   │   │   │   ├── charts.py
│   │   │   │   ├── insights.py
│   │   │   │   ├── chat.py
│   │   │   │   └── dashboards.py
│   │   │   └── websocket/
│   │   │       └── chat.py          # WebSocket for real-time chat
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── upload.py
│   │   │   ├── dataset.py
│   │   │   ├── metric.py
│   │   │   ├── chart.py
│   │   │   ├── insight.py
│   │   │   ├── conversation.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── schemas/                 # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── dataset.py
│   │   │   ├── metric.py
│   │   │   ├── chart.py
│   │   │   ├── insight.py
│   │   │   ├── chat.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── file_service.py      # Parse CSV / Excel
│   │   │   ├── dataset_service.py   # Store & manage datasets
│   │   │   ├── metric_service.py    # Calculate revenue metrics
│   │   │   ├── chart_service.py     # Generate chart configs
│   │   │   ├── insight_service.py   # Generate AI insights
│   │   │   └── chat_service.py      # Conversational AI
│   │   │
│   │   ├── ai/                      # AI pipeline
│   │   │   ├── __init__.py
│   │   │   ├── column_detector.py   # Detect revenue/date/category cols
│   │   │   ├── metric_calculator.py # Pandas aggregations
│   │   │   ├── insight_engine.py    # OpenAI prompt templates
│   │   │   ├── chart_recommender.py # Auto-select chart types
│   │   │   ├── chat_agent.py        # Chat with dataset context
│   │   │   └── prompts.py           # All prompt templates
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_parser.py       # CSV/Excel → DataFrame
│   │       └── formatters.py        # Number, date, currency
│   │
│   ├── alembic/                     # DB migrations
│   │   ├── versions/
│   │   └── alembic.ini
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_upload.py
│   │   ├── test_metrics.py
│   │   ├── test_insights.py
│   │   └── test_chat.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── docker/
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml
│       └── backend-ci.yml
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── API.md
│
├── .gitignore
└── README.md
```

---

## 2. Database Schema (PostgreSQL)

```sql
-- Users
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- File uploads
CREATE TABLE uploads (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    filename   VARCHAR(500) NOT NULL,
    file_type  VARCHAR(10) NOT NULL,        -- 'csv' | 'xlsx'
    file_size  BIGINT NOT NULL,
    status     VARCHAR(20) DEFAULT 'pending', -- pending | processing | ready | failed
    error_msg  TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Processed datasets
CREATE TABLE datasets (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id    UUID REFERENCES uploads(id) ON DELETE CASCADE,
    user_id      UUID REFERENCES users(id) ON DELETE CASCADE,
    name         VARCHAR(500) NOT NULL,
    row_count    INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    columns_meta JSONB,                     -- [{name, dtype, detected_role}]
    summary      JSONB,                     -- statistical summary
    status       VARCHAR(20) DEFAULT 'processing',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Calculated metrics
CREATE TABLE metrics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id  UUID REFERENCES datasets(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,       -- total_revenue | monthly_revenue | growth_rate | aov | top_product | etc.
    metric_name VARCHAR(255) NOT NULL,
    value       NUMERIC(20, 4),
    currency    VARCHAR(3) DEFAULT 'USD',
    period      VARCHAR(20),                -- '2024-01' | 'Q1-2024' | 'all'
    metadata    JSONB,                      -- extra context
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Chart configurations
CREATE TABLE charts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id  UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    chart_type  VARCHAR(50) NOT NULL,       -- line | bar | pie | area
    title       VARCHAR(255) NOT NULL,
    config      JSONB NOT NULL,             -- x_axis, y_axis, group_by, filters
    data        JSONB,                      -- cached chart data
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- AI-generated insights
CREATE TABLE insights (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id  UUID REFERENCES datasets(id) ON DELETE CASCADE,
    type        VARCHAR(50) NOT NULL,       -- trend | anomaly | opportunity | decline | recommendation
    title       VARCHAR(255) NOT NULL,
    content     TEXT NOT NULL,
    severity    VARCHAR(20) DEFAULT 'info', -- info | warning | critical
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Chat conversations
CREATE TABLE conversations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id  UUID REFERENCES datasets(id) ON DELETE CASCADE,
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    messages    JSONB NOT NULL DEFAULT '[]', -- [{role, content, timestamp, metadata?}]
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboards (user-saved layouts)
CREATE TABLE dashboards (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    layout      JSONB NOT NULL DEFAULT '[]', -- grid layout config
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_metrics_dataset ON metrics(dataset_id);
CREATE INDEX idx_insights_dataset ON insights(dataset_id);
CREATE INDEX idx_conversations_dataset ON conversations(dataset_id);
CREATE INDEX idx_charts_dataset ON charts(dataset_id);
CREATE INDEX idx_uploads_user ON uploads(user_id);
CREATE INDEX idx_datasets_user ON datasets(user_id);
```

---

## 3. Frontend Architecture

### Route Design (Next.js App Router)

```
/                         → Landing / marketing page
/dashboard                → Main dashboard (list of datasets, overview KPI)
/dashboard/[id]           → Dataset-specific dashboard
/upload                   → File upload page
/analytics/[id]           → Deep drill-down analytics
/analytics/[id]/chat      → AI chat scoped to a dataset
/settings                 → User settings
```

### Component Tree

```
<RootLayout>
  <ThemeProvider />
  <Sidebar />                     ← persistent nav
  <main>
    {children}                    ← page content
  </main>
</RootLayout>

Dashboard Page:
  <DashboardHeader />
  <KPIGrid>
    <KPICard icon="revenue" />
    <KPICard icon="growth" />
    <KPICard icon="orders" />
    <KPICard icon="aov" />
  </KPIGrid>
  <ChartGrid>
    <ChartContainer type="line" />
    <ChartContainer type="bar" />
    <ChartContainer type="pie" />
  </ChartGrid>
  <InsightPanel>
    <InsightCard severity="info" />
    <InsightCard severity="warning" />
  </InsightPanel>

Chat Page:
  <ChatLayout>
    <ChatMessageList />
    <ChatInput />
    <InsightSidePanel />
  </ChatLayout>
```

### State Management (Zustand)

```ts
// store/index.ts — slices:
- datasetStore:     currentDataset, datasetList, loading
- metricStore:      metricsByDataset, selectedMetric
- chartStore:       chartsByDataset, chartConfigs
- insightStore:     insightsByDataset
- chatStore:        conversations, activeMessages, streaming
- uiStore:          sidebarOpen, theme
```

### API Client Layer

```
lib/api-client.ts
  ├── uploadFile(file)          → POST /api/v1/upload
  ├── getDatasets()             → GET  /api/v1/datasets
  ├── getDataset(id)            → GET  /api/v1/datasets/:id
  ├── getMetrics(datasetId)     → GET  /api/v1/metrics/:datasetId
  ├── getInsights(datasetId)    → GET  /api/v1/insights/:datasetId
  ├── getCharts(datasetId)      → GET  /api/v1/charts/:datasetId
  ├── sendMessage(datasetId, msg) → POST /api/v1/chat/:datasetId
  └── wsChat(datasetId)         → ws://.../chat/:datasetId
```

### Data Flow

```
User uploads file
  → FileDropzone → api.uploadFile()
  → Backend processes (async) → status: processing → ready
  → Frontend polls status or receives webhook
  → Dashboard auto-populates with KPIs + charts + insights
  → User can chat about dataset
    → ChatInput → api.sendMessage() / WebSocket
    → Backend AI pipeline → response streamed to UI
```

---

## 4. Backend Services

### Service Layer Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI App                            │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │ Dataset  │  │  Metric  │  │  Chart   │   │
│  │  Router  │  │  Router  │  │  Router  │  │  Router  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │             │              │          │
│  ┌────▼──────────────▼─────────────▼──────────────▼─────┐   │
│  │                  Service Layer                        │   │
│  │  ┌────────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│  │  │file_service│ │dataset_  │ │metric_service    │    │   │
│  │  │            │ │service   │ │                  │    │   │
│  │  │ CSV/Excel  │ │store/    │ │aggregations,     │    │   │
│  │  │ parsing    │ │manage    │ │growth, trends    │    │   │
│  │  └────────────┘ └──────────┘ └──────────────────┘    │   │
│  │  ┌────────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│  │  │chart_service│ │insight_  │ │chat_service      │    │   │
│  │  │            │ │service   │ │                  │    │   │
│  │  │chart config│ │AI insight│ │conversational AI │    │   │
│  │  │generation  │ │engine    │ │with context      │    │   │
│  │  └────────────┘ └──────────┘ └──────────────────┘    │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                  AI Pipeline                          │    │
│  │  column_detector → metric_calculator → insight_engine │    │
│  │                    → chart_recommender → chat_agent   │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Service Responsibilities

| Service | Responsibility |
|---|---|
| `file_service.py` | Validate uploaded file, parse CSV/Excel into DataFrame, store raw data |
| `dataset_service.py` | Save dataset metadata, manage dataset lifecycle (processing → ready → failed) |
| `metric_service.py` | Run Pandas aggregations: total revenue, monthly breakdown, growth rate, AOV, top products, trends |
| `chart_service.py` | Generate Plotly/Recharts-compatible chart configs + cached data payloads |
| `insight_service.py` | Orchestrate AI insight generation → saves to DB |
| `chat_service.py` | Manage conversation state, call AI chat agent, stream responses |

### API Endpoints

```
POST   /api/v1/upload                      # Upload file (multipart)
GET    /api/v1/datasets                    # List user's datasets
GET    /api/v1/datasets/:id                # Get dataset detail
DELETE /api/v1/datasets/:id                # Delete dataset + data
GET    /api/v1/datasets/:id/preview        # First 50 rows as JSON
POST   /api/v1/datasets/:id/process        # Trigger AI processing

GET    /api/v1/metrics/:datasetId          # All metrics for dataset
GET    /api/v1/metrics/:datasetId/:type    # Filter by metric type

GET    /api/v1/charts/:datasetId           # Auto-generated charts
POST   /api/v1/charts                      # Save custom chart config
DELETE /api/v1/charts/:id

GET    /api/v1/insights/:datasetId         # All insights
PATCH  /api/v1/insights/:id/acknowledge    # Mark insight as seen

POST   /api/v1/chat/:datasetId             # Send message, get response
WS     /ws/chat/:datasetId                 # WebSocket for streaming chat

GET    /api/v1/dashboards                  # List dashboards
POST   /api/v1/dashboards                  # Save dashboard layout
PUT    /api/v1/dashboards/:id              # Update layout
DELETE /api/v1/dashboards/:id
```

---

## 5. AI Pipeline

### End-to-End Flow

```
┌────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│  File      │    │  Column      │    │  Metric         │    │  Insight     │
│  Upload    │───▶│  Detection   │───▶│  Calculator     │───▶│  Engine      │
│  (CSV/xlsx)│    │              │    │                 │    │              │
└────────────┘    └──────────────┘    └────────────────┘    └──────┬───────┘
                                                                  │
         ┌──────────────────────────────┐                         │
         │  Chart Recommender           │◀────────────────────────┘
         │  (auto-select viz type)      │
         └──────────┬───────────────────┘
                    │
         ┌──────────▼───────────────────┐
         │  Chat Agent                  │
         │  (conversational Q&A)        │
         └──────────────────────────────┘
```

### Step-by-Step Pipeline

#### Step 1: File Upload & Parsing
```
Input:  CSV or .xlsx file
Action: file_service.py parses with Pandas
Output: pd.DataFrame + metadata (rows, cols, dtypes)
```

#### Step 2: Column Detection (AI + Heuristic)
```
Input:  DataFrame columns + sample rows
Action: column_detector.py classifies columns:

        ┌──────────────────┬────────────────────────────────┐
        │ Role             │ Heuristic                      │
        ├──────────────────┼────────────────────────────────┤
        │ revenue          │ contains: revenue, sales,      │
        │                  │ income, amount, price * qty    │
        │ quantity         │ contains: qty, quantity, units │
        │ unit_price       │ contains: price, rate, cost    │
        │ date             │ datetime dtype or keyword      │
        │ category         │ low-cardinality string cols    │
        │ product          │ contains: product, name, item  │
        │ customer         │ contains: customer, client     │
        │ discount         │ contains: discount, promo      │
        │ id               │ id, key, code                  │
        └──────────────────┴────────────────────────────────┘

        Uses OpenAI to confirm ambiguous columns.
Output: ColumnRoleMap: {col_name: "revenue" | "date" | "category" | ...}
```

#### Step 3: Metric Calculation (Pandas)
```
Input:  DataFrame + ColumnRoleMap
Action: metric_calculator.py runs:

        Metrics calculated:
        ├── Total Revenue           → df[revenue_col].sum()
        ├── Monthly Revenue         → groupby(month(df[date_col]))[revenue].sum()
        ├── Revenue Growth Rate     → (current_month - prev_month) / prev_month
        ├── Average Order Value     → total_revenue / order_count
        ├── Top Products            → groupby(product_col)[revenue].sum().nlargest(10)
        ├── Category Breakdown      → groupby(category_col)[revenue].sum()
        ├── Sales Trends            → rolling average, % change
        ├── Anomaly Detection       → z-score, % deviation from mean
        └── Data Quality            → nulls %, duplicates

Output: MetricResult[] (stored in metrics table)
```

#### Step 4: Insight Generation (OpenAI)
```
Input:  MetricResult[] + dataset summary + ColumnRoleMap
Action: insight_engine.py builds prompt:

        System Prompt:
          "You are RevenueAI, an expert business analyst. Analyze the
           following dataset metrics and generate actionable business
           insights. For each insight, provide: type (trend/anomaly/
           opportunity/decline/recommendation), title, detailed
           explanation, and severity."

        Context injected:
          - Dataset shape: {rows} x {cols}
          - Columns detected: {roles}
          - Key metrics: {total_revenue, growth_rate, aov, top_products}
          - Trends: {monthly_trend, category_performance}

        Response format (JSON):
        {
          "insights": [
            {
              "type": "trend",
              "title": "Revenue grew 23% month-over-month",
              "content": "...",
              "severity": "info"
            },
            ...
          ]
        }

Output: Insight[] (stored in insights table)
```

#### Step 5: Chart Recommendation
```
Input:  DataFrame + ColumnRoleMap + MetricResult[]
Action: chart_recommender.py auto-selects:

        ┌──────────────────┬─────────────────────────────┐
        │ Visualization    │ When                        │
        ├──────────────────┼─────────────────────────────┤
        │ Line Chart       │ revenue over time           │
        │ Bar Chart        │ top products, categories    │
        │ Pie Chart        │ category breakdown (%)       │
        │ Area Chart       │ cumulative revenue           │
        │ KPI Card         │ total revenue, growth rate  │
        │ Heatmap          │ revenue by month + category │
        └──────────────────┴─────────────────────────────┘

Output: ChartConfig[] (stored in charts table + returned to frontend)
```

#### Step 6: Chat Agent (Conversational AI)
```
Input:  User question + dataset context
Action: chat_agent.py:

        1. Retrieve dataset context:
           - Column roles
           - Metric summary
           - Recent insights
           - Sample rows (first 5)

        2. Build context-aware prompt:
           """
           You are RevenueAI, an AI business analyst.
           Dataset: {name} ({rows} rows, {cols} columns)
           Columns: {column_roles}
           Key Metrics: {metrics_summary}
           Insights: {insights}

           Chat History:
           {last N messages}

           User: {question}
           Assistant:
           """

        3. OpenAI streaming response
           - Returns text chunks via WebSocket / SSE
           - May include inline data (metric values, chart references)

        4. Persist conversation (messages appended to conversations table)

Output: Streamed text response + optional structured data
```

### OpenAI Integration Strategy

```
┌────────────────────────────────────────────────────────────┐
│                 OpenAI (GPT-4 / GPT-4o)                     │
│                                                            │
│  Calls:                                                     │
│   1. Column Detection        — low temp (0.1), JSON mode   │
│   2. Insight Generation      — medium temp (0.3), JSON     │
│   3. Chart Recommendation    — medium temp (0.3), JSON     │
│   4. Chat Response           — high temp (0.7), streaming  │
│                                                            │
│  Token Budget per pipeline run:                            │
│   - Column detection:     ~500 tokens                      │
│   - Insight generation:  ~2000 tokens                      │
│   - Chart recommendation:  ~800 tokens                     │
│   - Chat message:        ~500-1500 tokens                  │
│                                                            │
│  Caching:                                                   │
│   - Column detection is cached per unique column set       │
│   - Insight prompts are cached with hash of metrics        │
│                                                            │
│  Fallback:                                                  │
│   - If OpenAI is unavailable, use pure heuristic mode       │
│   - Column detection falls back to regex + dtype inference  │
│   - Insights use template-based generation                  │
└────────────────────────────────────────────────────────────┘
```

### Async Processing

```
1. User uploads file
2. API returns 202 Accepted + upload_id
3. Background task (FastAPI BackgroundTasks / Celery):
   a. Parse file → DataFrame
   b. Detect columns
   c. Calculate metrics
   d. Generate insights
   e. Recommend charts
   f. Update status → "ready"
4. Frontend polls GET /datasets/:id or receives push notification
5. UI refreshes with charts, KPIs, and insights
```

---

## Data Flow Summary

```
User Uploads CSV
    │
    ▼
frontend/api.uploadFile() ───── POST /api/v1/upload ───── FastAPI
                                                              │
                                                              ▼
                                                    file_service.parse()
                                                              │
                                                              ▼
                                                    column_detector.detect()
                                                              │
                                                              ▼
                                                    metric_calculator.calculate()
                                                              │
                                                              ▼
                                          ┌───────────────────┼───────────────────┐
                                          ▼                   ▼                   ▼
                                   insight_engine     chart_recommender    (save to DB)
                                          │                   │
                                          └───────────────────┘
                                                              │
                                                              ▼
                                                     status → "ready"
                                                              │
                                                              ▼
Frontend polls ────────────────── GET /api/v1/datasets/:id ──┐
  (or websocket)                                              │
                                                              ▼
                                          Dashboard renders with:
                                          - KPI Cards
                                          - Charts
                                          - Insights
                                          - Chat ready
```

---

## Security & Auth

- **Auth**: JWT-based authentication (access + refresh tokens)
- **User isolation**: All queries scoped by `user_id`
- **File validation**: MIME type, size limit (50MB), malware scan header
- **API rate limiting**: 100 req/min per user (chat: 20 req/min)
- **OpenAI key**: Server-side only, never exposed to frontend

# Claude Code Usage Analytics Platform

End-to-end analytics platform that processes telemetry data from Claude Code sessions, transforming raw event streams into actionable insights through an interactive dashboard, REST API, and ML-powered forecasting.

## Project Structure

```
├── config.py                      # Paths configuration
├── run_ingestion.py               # Data ingestion entry point
├── requirements.txt               # Dependencies
│
├── Given_Material/                # Provided assignment materials
│   ├── generate_fake_data.py
│   └── README.md
│
├── data/
│   ├── raw/                       # Generated telemetry (JSONL + CSV)
│   └── analytics.db               # SQLite database
│
├── src/
│   ├── ingestion/                 # Data pipeline
│   │   ├── parser.py              # Stream-parse JSONL telemetry
│   │   ├── validator.py           # Validation rules + statistics
│   │   └── loader.py              # Batch load into SQLite
│   │
│   ├── database/                  # Storage layer
│   │   ├── schema.py              # 6 tables, 15 indexes
│   │   ├── connection.py          # Connection management (WAL mode)
│   │   └── queries.py             # Query helpers
│   │
│   ├── analytics/                 # Analytics engine
│   │   ├── token_usage.py         # Token & cost analysis
│   │   ├── session_patterns.py    # Session & user behavior
│   │   ├── tool_usage.py          # Tool usage & errors
│   │   ├── advanced_stats.py      # Correlations, cohorts, efficiency
│   │   ├── forecasting.py         # ML forecasting & anomaly detection
│   │   └── realtime.py            # Real-time streaming simulation
│   │
│   └── api/
│       └── endpoints.py           # FastAPI (18 routes)
│
├── dashboard/                     # Streamlit dashboard
│   ├── app.py                     # Entry point
│   ├── pages/
│   │   ├── overview.py            # KPIs & daily trends
│   │   ├── token_analysis.py      # Cost by model/practice/level
│   │   ├── tool_analysis.py       # Tool frequency, errors
│   │   ├── user_analysis.py       # Engagement, session durations
│   │   ├── advanced_stats.py      # Cohorts, correlations, efficiency
│   │   ├── predictions.py         # Forecasting & anomalies
│   │   └── realtime.py            # Live streaming demo
│   └── components/
│       ├── charts.py              # Plotly chart builders
│       └── metrics.py             # KPI card renderers
│
└── tests/
    ├── test_ingestion.py
    ├── test_database.py
    └── test_analytics.py
```

## Setup

### Prerequisites

- Python 3.10+

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate data

```bash
python Given_Material/generate_fake_data.py --num-users 100 --num-sessions 5000 --days 60 --output-dir data/raw
```

### 3. Run ingestion

```bash
python run_ingestion.py
```

Parses ~454K events from JSONL, validates each record, loads into SQLite at ~19K events/sec.

### 4. Launch dashboard

```bash
streamlit run dashboard/app.py
```

### 5. Launch API (optional)

```bash
uvicorn src.api.endpoints:app --reload --port 8000
```

Docs at `http://localhost:8000/docs`

### 6. Run tests

```bash
python tests/test_ingestion.py
python tests/test_database.py
python tests/test_analytics.py
```

## Data Pipeline

```
JSONL (521 MB) → Stream parse → Validate → Batch INSERT → SQLite
                                                            ↓
                                              Analytics (SQL + pandas)
                                                            ↓
                                                ML (scikit-learn)
                                                            ↓
                                              Dashboard / API
```

## Dashboard Pages

| Page | Description |
|------|-------------|
| **Overview** | KPIs, daily cost/request trends, hourly patterns, error summary |
| **Token & Cost** | Model breakdown, practice/level comparison, top spenders |
| **Tool & Error** | Tool frequency, success rates, heatmap by practice, error trends |
| **User & Session** | Engagement scatter, DAU, session duration distribution |
| **Advanced Stats** | Cohort analysis, efficiency scores, correlations, complexity |
| **Predictions** | Linear regression forecast, Isolation Forest anomaly detection |
| **Real-Time** | Live streaming simulation with rolling metrics |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/summary` | High-level stats |
| `GET /api/tokens/daily` | Daily token consumption |
| `GET /api/tokens/by-model` | Breakdown by model |
| `GET /api/tokens/by-practice` | Breakdown by practice |
| `GET /api/tokens/by-level` | Breakdown by seniority |
| `GET /api/tokens/hourly-pattern` | Hourly usage pattern |
| `GET /api/users/cost` | Cost per user |
| `GET /api/users/sessions` | Sessions per user |
| `GET /api/users/daily-active` | DAU counts |
| `GET /api/users/weekly-engagement` | Weekly metrics |
| `GET /api/tools/usage` | Tool usage stats |
| `GET /api/tools/decisions` | Accept/reject decisions |
| `GET /api/errors` | Error analysis |
| `GET /api/forecast/cost?days=14` | Cost forecast |
| `GET /api/anomalies?sensitivity=0.05` | Anomaly detection |
| `GET /api/growth` | Week-over-week growth |

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Dashboard |
| `pandas` | Data processing |
| `plotly` | Charts |
| `scikit-learn` | ML (forecasting, anomaly detection) |
| `fastapi` | REST API |
| `uvicorn` | ASGI server |
| `numpy` | Numerical operations |

## LLM Usage Log

Built using **Claude Code (Claude Opus 4.6)**.

### Key prompts
1. **Architecture**: "Build an end-to-end analytics platform with professional structure for Claude Code telemetry"
2. **Data pipeline**: Stream parser + validator + batch loader for 500MB+ JSONL
3. **Analytics**: SQL-based analytics for tokens, sessions, tools; ML forecasting + anomaly detection
4. **Dashboard**: 7-page Streamlit app with Plotly charts
5. **API**: FastAPI endpoints with OpenAPI docs

### Validation
- 27 unit tests covering ingestion, database, and analytics — all passing
- 100% validation rate on 454,428 events
- Verified SQL queries against raw data
- Confirmed ingestion at ~19K events/sec

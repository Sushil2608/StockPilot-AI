<div align="center">

# StockPilot AI

### An Agentic AI-powered Stock Research Assistant

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-1.x-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.x-FF6F00?style=flat)](https://langchain-ai.github.io/langgraph/)
[![Claude](https://img.shields.io/badge/Claude-Anthropic-D97757?style=flat)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<br />

StockPilot AI is a multi-agent system that researches publicly traded companies using specialized AI agents. Given a stock ticker, it runs **parallel research** across financial data, news sentiment, and technical analysis — then synthesizes everything into a comprehensive **investment report with a 12-month price target**.

Supports both **US (NYSE/NASDAQ)** and **Indian (NSE)** markets.

<br />

[Getting Started](#getting-started) · [Architecture](#architecture) · [Features](#key-features) · [Tech Stack](#tech-stack) · [API Reference](#api-reference) · [Roadmap](#future-roadmap)

</div>

<br />

---

## Key Features

### AI & Analysis
- **Multi-Agent Orchestration** — LangGraph StateGraph coordinates 5 specialized agents with parallel execution
- **Piotroski F-Score** — All 9 criteria computed from live financial statements (profitability, leverage, efficiency)
- **Composite Technical Score (0-100)** — Weighted scoring from RSI, MACD, Bollinger Bands, SMA/EMA, and volume
- **Blended Price Target** — 12-month target from 4 methods: PE-forward, technical momentum, 52W mean-reversion, score-adjusted
- **LangChain Tool Use** — Report Writer uses `bind_tools()` with 3 quantitative analysis tools
- **Graceful Degradation** — Each agent is independently fault-tolerant; one failure doesn't stop the pipeline

### Markets
- **US Markets** — NYSE/NASDAQ tickers (AAPL, NVDA, MSFT…)
- **Indian Markets** — NSE tickers with auto `.NS` suffix (RELIANCE, TCS, INFY…)
- **Dual Currency** — USD ($) with B/M/K formatting; INR (₹) with Cr/L formatting

### UI & Data
- **Dark Mode Dashboard** — Glassmorphism design with framer-motion animations
- **Interactive Price Chart** — Area, Line, and Candlestick chart types
- **Multi-Period History** — 5D (5-min), 1M, 3M, 6M, 1Y (daily), 5Y (weekly)
- **Volume Bars** — Shown below the main chart, color-coded by candle direction
- **Real-time Progress** — SSE streaming with per-agent status, elapsed time counter
- **Ticker Validation** — Invalid tickers return a 400 before consuming any LLM tokens

---

## Architecture

```
                        ┌──────────────────────────────────────────────┐
                        │           Frontend (Next.js 15)              │
                        │  Market Selector → Ticker → Live Progress    │
                        │  Area/Line/Candle Chart · Period Toggles     │
                        └─────────────────┬────────────────────────────┘
                                          │ SSE / REST
                        ┌─────────────────▼────────────────────────────┐
                        │            FastAPI Backend                    │
                        │                                              │
                        │   ┌──────────────────────────────────────┐   │
                        │   │        LangGraph Workflow             │   │
                        │   │                                      │   │
                        │   │         ┌──────────┐                 │   │
                        │   │         │ Planner  │                 │   │
                        │   │         └────┬─────┘                 │   │
                        │   │   ┌──────────┼──────────┐            │   │
                        │   │   ▼          ▼          ▼            │   │
                        │   │ ┌────────┐┌──────┐┌──────────┐       │   │
                        │   │ │Finance ││ News ││Technical │       │   │
                        │   │ │ Agent  ││Agent ││  Agent   │       │   │
                        │   │ │F-Score ││Senti-││Score 0-  │       │   │
                        │   │ │9 pts   ││ment  ││100 pts   │       │   │
                        │   │ └───┬────┘└──┬───┘└────┬─────┘       │   │
                        │   │     └────────┼─────────┘             │   │
                        │   │              ▼                       │   │
                        │   │   ┌──────────────────────┐           │   │
                        │   │   │    Report Writer      │           │   │
                        │   │   │  3 LangChain Tools:   │           │   │
                        │   │   │  · Valuation          │           │   │
                        │   │   │  · Risk Assessment    │           │   │
                        │   │   │  · Price Target       │           │   │
                        │   │   └──────────────────────┘           │   │
                        │   └──────────────────────────────────────┘   │
                        │                                              │
                        │   Data: yfinance · LLM: Claude · TA: ta-lib │
                        └──────────────────────────────────────────────┘
```

> Financial, News, and Technical agents run **in parallel** via LangGraph's fan-out, then converge into the Report Writer.

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Framer Motion |
| **Backend** | Python 3.12, FastAPI, Pydantic, asyncio |
| **AI / LLM** | LangChain, LangGraph, Claude (Anthropic API) |
| **Finance Data** | yfinance, pandas, numpy, ta-lib |
| **Streaming** | Server-Sent Events (SSE) via sse-starlette |
| **Deployment** | Docker, docker-compose |
| **Testing** | pytest, pytest-asyncio |

---

## Project Structure

```
stockpilot-ai/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── planner.py           # Research plan via Claude
│   │   │   ├── financial.py         # yfinance data + Piotroski F-Score
│   │   │   ├── news.py              # News fetch + LLM sentiment analysis
│   │   │   ├── technical.py         # ta-lib indicators + composite score (0-100)
│   │   │   └── report_writer.py     # Synthesis with 3 LangChain tools + price target
│   │   ├── workflows/
│   │   │   └── research.py          # LangGraph StateGraph, parallel fan-out
│   │   ├── schemas/                 # Pydantic models for every agent I/O
│   │   ├── services/
│   │   │   ├── llm.py               # ChatAnthropic factory with retry
│   │   │   └── ticker.py            # Ticker validation service
│   │   ├── api/
│   │   │   └── routes.py            # REST + SSE endpoints, price history
│   │   ├── config.py                # Pydantic Settings
│   │   └── main.py                  # FastAPI app
│   ├── tests/                       # pytest suite (22 tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx             # Main dashboard
│   │   ├── components/
│   │   │   ├── price-chart.tsx      # Area/Line/Candle + period selector
│   │   │   ├── financial-card.tsx   # Metrics + F-Score visualization
│   │   │   ├── technical-card.tsx   # Indicators + score progress bar
│   │   │   ├── report-card.tsx      # Report + price target display
│   │   │   ├── news-card.tsx        # Sentiment + clickable sources
│   │   │   ├── search-bar.tsx       # Ticker input + US/IN market toggle
│   │   │   └── progress-tracker.tsx # Live agent status + elapsed time
│   │   └── lib/                     # Types, API client, formatters
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Anthropic API key** — [Get one here](https://console.anthropic.com/)

### 1. Clone & Configure

```bash
git clone https://github.com/Sushil2608/StockPilot-AI.git
cd StockPilot-AI

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Run Locally

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**, select a market (US or IN), enter a ticker, and hit Analyze.

### 3. Run with Docker

```bash
docker compose up --build
```

Backend on `http://localhost:8000` · Frontend on `http://localhost:3000`

---

## Environment Variables

| Variable | Required | Default | Description |
|:---------|:--------:|:--------|:------------|
| `ANTHROPIC_API_KEY` | **Yes** | — | Your Anthropic API key |
| `MODEL_NAME` | No | `claude-sonnet-4-6` | Claude model to use |
| `MODEL_TEMPERATURE` | No | `0.3` | LLM temperature (0.0–1.0) |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `BACKEND_PORT` | No | `8000` | Backend server port |
| `FRONTEND_PORT` | No | `3000` | Frontend server port |

---

## API Reference

### Endpoints

| Method | Path | Description |
|:-------|:-----|:------------|
| `GET` | `/` | Application info |
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Full analysis — JSON response |
| `POST` | `/analyze/stream` | Full analysis — SSE streaming |
| `GET` | `/price-history/{ticker}` | OHLCV price history by period |

### Price History Parameters

```
GET /price-history/AAPL?period=1y&market=US
GET /price-history/RELIANCE?period=6mo&market=IN
```

| Period | Interval | Description |
|:-------|:---------|:------------|
| `5d` | 5-min | Last 5 trading days, intraday |
| `1mo` | Daily | Last month |
| `3mo` | Daily | Last 3 months |
| `6mo` | Daily | Last 6 months |
| `1y` | Daily | Last year |
| `5y` | Weekly | Last 5 years |

### Example: Analyze a Stock

```bash
# US market
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA", "market": "US"}'

# Indian market
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "RELIANCE", "market": "IN"}'
```

<details>
<summary><strong>Response Schema</strong></summary>

```json
{
  "ticker": "NVDA",
  "market": "US",
  "currency": "USD",
  "financial": {
    "current_price": 162.15,
    "revenue_growth": 122.4,
    "profit_margin": 55.0,
    "piotroski_score": 7,
    "fundamental_signal": "healthy",
    "piotroski_details": ["Positive ROA", "Positive operating cash flow", "..."]
  },
  "technical": {
    "rsi": 58.3,
    "macd": 1.25,
    "technical_score": 72,
    "trend": "bullish",
    "score_breakdown": {"rsi": 12, "macd": 20, "moving_avg": 25, "bollinger": 9, "volume": 8}
  },
  "report": {
    "recommendation": "Buy",
    "confidence_score": 0.82,
    "target_price": 185.40,
    "target_upside": 14.3,
    "target_methodology": "Blended: PE-forward (35%), score-adjusted (30%), momentum (20%), 52W reversion (15%)",
    "summary": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "risks": ["..."]
  }
}
```

</details>

---

## How It Works

```
1. User selects market (US / IN) and enters ticker
   │
2. Ticker validation — 400 returned immediately for invalid symbols
   │
3. Planner Agent creates a structured research plan
   │
4. Three agents run IN PARALLEL:
   ├── Financial Agent  →  yfinance fundamentals + Piotroski F-Score (0-9)
   ├── News Agent       →  yfinance news → LLM sentiment analysis
   └── Technical Agent  →  RSI, MACD, Bollinger, EMA, ATR → composite score (0-100)
   │
5. Report Writer calls 3 LangChain tools:
   ├── calculate_valuation    →  PE, margins, growth assessment
   ├── assess_risk_level      →  D/E, RSI, ATR, FCF risk scoring
   └── compute_price_target   →  Blended 12-month target (4 methods)
   │
6. Final report: recommendation, confidence, target price, strengths/weaknesses/risks
   │
7. Dashboard renders with animated cards, interactive chart, F-Score bar
```

---

## Scoring Systems

### Piotroski F-Score (Financial Agent)

9 binary criteria across 3 dimensions — each scores 0 or 1:

| Dimension | Criteria |
|:----------|:---------|
| **Profitability** | Positive ROA, Positive OCF, Rising ROA, Cash > Accrual earnings |
| **Leverage & Liquidity** | Declining leverage, Current ratio ≥ 1, No share dilution |
| **Efficiency** | Rising gross margin, Rising asset turnover |

**Signal mapping:** 8-9 → Strong · 6-7 → Healthy · 4-5 → Neutral · 2-3 → Weak · 0-1 → Distressed

### Technical Score (Technical Agent)

Composite 0-100 score with weighted signal components:

| Component | Max Points | Signal |
|:----------|:----------:|:-------|
| RSI (14) | 25 | Oversold → bullish; Overbought → bearish |
| MACD + Histogram | 25 | Crossover direction + momentum |
| SMA 50 / 200 alignment | 25 | Price position vs golden/death cross |
| Bollinger Band position | 15 | %B position within bands |
| Volume confirmation | 10 | Current vs 20-day average |

**Score → Trend:** 65+ Bullish · 36-64 Neutral · ≤35 Bearish

### Price Target Methodology

Blended 12-month target from 4 quantitative methods:

| Method | Weight | Basis |
|:-------|:------:|:------|
| PE-forward | 35% | Forward EPS × growth-adjusted PE |
| Score-adjusted | 30% | Combined F-Score + Technical Score multiplier |
| Technical momentum | 20% | SMA alignment → upside/downside trajectory |
| 52W mean-reversion | 15% | Midpoint + 30% toward 52-week high |

---

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

```
tests/test_financial_agent.py   9 tests  ✓  ROE, margins, D/E, dividends
tests/test_health.py            4 tests  ✓  API endpoints and validation
tests/test_technical_agent.py   9 tests  ✓  Scoring, signals, edge cases

22 passed
```

---

## Screenshots

> Screenshots coming soon — run the app locally to see the dashboard in action.

---

## Future Roadmap

- [ ] Portfolio analysis across multiple stocks
- [ ] Investment committee — multi-agent debate system
- [ ] RAG over earnings call transcripts
- [ ] SEC / BSE filings analysis (10-K, 10-Q, annual reports)
- [ ] Vector database for research memory
- [ ] Backtesting recommendations against historical data
- [ ] Altman Z-Score and DCF valuation
- [ ] Price alerts and notifications

---

## Disclaimer

This project is for **educational and demonstration purposes only**. It is not financial advice. Always do your own research and consult a qualified financial advisor before making investment decisions.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with LangChain, LangGraph, and Claude · [GitHub](https://github.com/Sushil2608/StockPilot-AI)

</div>

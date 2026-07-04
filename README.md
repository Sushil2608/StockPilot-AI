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

StockPilot AI is a multi-agent system that researches publicly traded companies using specialized AI agents. Given a stock ticker, it runs **parallel research** across financial data, news sentiment, and technical analysis — then synthesizes everything into a comprehensive **investment report**.

<br />

[Getting Started](#getting-started) · [Architecture](#architecture) · [Tech Stack](#tech-stack) · [API Reference](#api-reference) · [Roadmap](#future-roadmap)

</div>

<br />

---

## Key Features

- **Multi-Agent Orchestration** — LangGraph workflow coordinates 5 specialized agents with parallel execution
- **Planner Agent** — Creates a structured research plan for any stock ticker
- **Financial Agent** — Collects revenue, market cap, P/E ratio, EPS, cash, debt, ROE via yfinance
- **News Agent** — Fetches and summarizes recent news with LLM-powered sentiment analysis
- **Technical Analysis Agent** — Calculates RSI, MACD, SMA 50/200, and overall trend using the `ta` library
- **Report Writer Agent** — Synthesizes all research into an investment report with a confidence score
- **Real-time Streaming** — Server-Sent Events (SSE) stream each agent's progress to the frontend as it completes
- **Modern Dashboard** — Responsive Next.js frontend with interactive Recharts visualizations

---

## Architecture

```
                        ┌──────────────────────────────────────────────┐
                        │           Frontend (Next.js 15)              │
                        │    Ticker Input → Progress → Dashboard       │
                        └─────────────────┬────────────────────────────┘
                                          │ SSE / REST
                        ┌─────────────────▼────────────────────────────┐
                        │            FastAPI Backend                   │
                        │                                              │
                        │   ┌──────────────────────────────────────┐   │
                        │   │        LangGraph Workflow            │   │
                        │   │                                      │   │
                        │   │         ┌──────────┐                 │   │
                        │   │         │ Planner  │                 │   │
                        │   │         └────┬─────┘                 │   │
                        │   │              │                       │   │
                        │   │     ┌────────┼────────┐              │   │
                        │   │     ▼        ▼        ▼              │   │
                        │   │ ┌────────┐┌──────┐┌──────────┐       │   │
                        │   │ │Finance ││ News ││Technical │       │   │
                        │   │ │ Agent  ││Agent ││  Agent   │       │   │
                        │   │ └───┬────┘└──┬───┘└────┬─────┘       │   │
                        │   │     └────────┼─────────┘             │   │
                        │   │              ▼                       │   │
                        │   │      ┌──────────────┐                │   │
                        │   │      │Report Writer │                │   │
                        │   │      └──────────────┘                │   │
                        │   └──────────────────────────────────────┘   │
                        │                                              │
                        │   Data: yfinance │ LLM: Claude │ TA: ta     │
                        └──────────────────────────────────────────────┘
```

> Financial, News, and Technical agents run **in parallel** via LangGraph's fan-out, then converge into the Report Writer.

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | Python 3.12, FastAPI, Pydantic, asyncio |
| **AI / LLM** | LangChain, LangGraph, Claude (Anthropic API) |
| **Finance Data** | yfinance, pandas, numpy, ta |
| **Streaming** | Server-Sent Events (SSE) via sse-starlette |
| **Deployment** | Docker, docker-compose |
| **Testing** | pytest, pytest-asyncio |

---

## Project Structure

```
stockpilot-ai/
├── backend/
│   ├── app/
│   │   ├── agents/              # Individual AI agents
│   │   │   ├── planner.py       # Research planning (LangChain chain)
│   │   │   ├── financial.py     # Financial data collection (yfinance)
│   │   │   ├── news.py          # News analysis (LangChain chain)
│   │   │   ├── technical.py     # Technical indicators (ta library)
│   │   │   └── report_writer.py # Report synthesis (LangChain chain)
│   │   ├── workflows/
│   │   │   └── research.py      # LangGraph StateGraph with parallel execution
│   │   ├── schemas/             # Pydantic models (contracts for every agent)
│   │   ├── services/
│   │   │   └── llm.py           # LangChain ChatAnthropic factory
│   │   ├── api/
│   │   │   └── routes.py        # FastAPI endpoints + SSE streaming
│   │   ├── config.py            # Pydantic Settings
│   │   └── main.py              # FastAPI application
│   ├── tests/                   # pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx         # Main dashboard
│   │   ├── components/          # UI components (shadcn/ui + custom)
│   │   └── lib/                 # Types, API client, formatters
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
git clone https://github.com/yourusername/stockpilot-ai.git
cd stockpilot-ai

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

**Frontend** (in a separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**, enter a ticker (e.g. `NVDA`), and hit Analyze.

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
| `MODEL_TEMPERATURE` | No | `0.3` | LLM temperature (0.0 – 1.0) |
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
| `POST` | `/analyze` | Run full stock analysis (JSON response) |
| `POST` | `/analyze/stream` | Run analysis with SSE progress streaming |

### Example: Analyze a Stock

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA"}'
```

<details>
<summary><strong>Response Schema</strong></summary>

```json
{
  "ticker": "NVDA",
  "planner": {
    "ticker": "NVDA",
    "company_name": "NVIDIA Corporation",
    "steps": ["Research Financials", "Analyze News", "Technical Analysis", "Write Report"]
  },
  "financial": {
    "ticker": "NVDA",
    "company_name": "NVIDIA Corporation",
    "revenue": 130497000000,
    "market_cap": 3400000000000,
    "pe_ratio": 55.2,
    "eps": 2.94,
    "cash": 34800000000,
    "debt": 9710000000,
    "roe": 115.66,
    "current_price": 162.15
  },
  "news": {
    "ticker": "NVDA",
    "positive_developments": ["..."],
    "negative_developments": ["..."],
    "overall_sentiment": "bullish",
    "evidence": [{"title": "...", "source": "...", "url": "..."}]
  },
  "technical": {
    "ticker": "NVDA",
    "rsi": 58.32,
    "macd": 1.25,
    "sma_50": 155.40,
    "sma_200": 138.20,
    "trend": "bullish"
  },
  "report": {
    "ticker": "NVDA",
    "summary": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "risks": ["..."],
    "recommendation": "Buy",
    "confidence_score": 0.82
  }
}
```

</details>

### Example: SSE Streaming

```bash
curl -N -X POST http://localhost:8000/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

Events streamed in real-time:
```
event: agent_status
data: {"agent": "Planner", "status": "completed", "message": ""}

event: result_planner
data: {"ticker": "AAPL", "steps": [...]}

event: agent_status
data: {"agent": "Financial Agent", "status": "completed", "message": ""}

event: complete
data: { ... full response ... }
```

---

## How It Works

```
1. User enters a ticker (e.g., NVDA)
   │
2. Planner Agent creates a research plan
   │
3. Three agents run IN PARALLEL:
   ├── Financial Agent  →  yfinance data (revenue, PE, EPS, etc.)
   ├── News Agent       →  yfinance news → Claude summarization
   └── Technical Agent  →  ta library (RSI, MACD, SMA 50/200)
   │
4. Report Writer Agent synthesizes all evidence
   │
5. Dashboard displays results with real-time progress
```

---

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

```
tests/test_financial_agent.py::test_compute_roe_from_values     PASSED
tests/test_financial_agent.py::test_compute_roe_zero_equity      PASSED
tests/test_financial_agent.py::test_compute_roe_missing_fields   PASSED
tests/test_financial_agent.py::test_compute_roe_fallback         PASSED
tests/test_health.py::test_root                                  PASSED
tests/test_health.py::test_health                                PASSED
tests/test_health.py::test_analyze_invalid_ticker                PASSED
tests/test_health.py::test_analyze_missing_body                  PASSED
tests/test_technical_agent.py::test_safe_float_normal            PASSED
tests/test_technical_agent.py::test_safe_float_nan               PASSED
tests/test_technical_agent.py::test_safe_float_none              PASSED
tests/test_technical_agent.py::test_safe_float_numpy_nan         PASSED
tests/test_technical_agent.py::test_determine_trend_bullish      PASSED
tests/test_technical_agent.py::test_determine_trend_bearish      PASSED
tests/test_technical_agent.py::test_determine_trend_neutral      PASSED

15 passed
```

---

## Screenshots

> Screenshots coming soon — run the app locally to see the dashboard in action.

---

## Future Roadmap

- [ ] Portfolio analysis across multiple stocks
- [ ] Investment committee — multi-agent debate system
- [ ] RAG over earnings call transcripts
- [ ] SEC filings analysis (10-K, 10-Q)
- [ ] Vector database for research memory
- [ ] Backtesting recommendations against historical data
- [ ] Price alerts and email notifications

---

## Disclaimer

This project is for **educational and demonstration purposes only**. It is not financial advice. Always do your own research and consult a qualified financial advisor before making investment decisions.

---

## License

MIT

---

<div align="center">

Built with LangChain, LangGraph, and Claude

</div>

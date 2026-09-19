# Bitcoin Trading Agent

An AI-assisted Bitcoin trading system designed for **paper trading**, strategy evaluation, portfolio monitoring, and market analysis. The project combines a Python trading engine and FastAPI backend with a React/Vite dashboard.

> **Disclaimer:** This project is for educational and research purposes. It is configured for paper trading and does not place real Coinbase orders. Cryptocurrency trading involves substantial risk.

## Overview

The Bitcoin Trading Agent brings together:

- Real-time BTC market data
- Technical indicators including RSI, MACD, ATR, and volume
- Dollar-cost averaging (DCA)
- ATR-based trading signals and stop-loss calculations
- Risk management and position limits
- A hybrid decision layer combining deterministic strategies with an LLM advisor
- Paper-trading execution and portfolio tracking
- Trade logging and performance reporting
- Telegram trade notifications
- A React dashboard for monitoring the system
- Backtesting and performance-analysis notebooks
- ChromaDB support for the AI/LLM workflow

## Architecture

```
bitcoin-trader/
├── app/
│   ├── strategies/             # Trading strategies
│   ├── trading_agent.py        # Main trading orchestrator
│   ├── paper_trading_engine.py # Simulated trade execution
│   ├── risk_manager.py         # Portfolio and trade risk controls
│   ├── market_data.py          # BTC market-data retrieval
│   ├── llm_advisor.py          # LLM market analysis
│   ├── telegram_notifier.py    # Trade notifications
│   ├── trade_logger.py         # Trade history
│   ├── backtester.py           # Backtesting
│   └── *.ipynb                 # Research and analysis notebooks
├── backend/
│   └── main.py                 # FastAPI API
├── frontend/
│   └── src/                    # React dashboard
├── data/                       # Data files
├── logs/                       # Trading logs
├── requirements.txt
└── .gitignore
```

## Key Components

### Trading Agent

`app/trading_agent.py` orchestrates the trading workflow:

1. Receives market observations.
2. Updates the paper-trading engine.
3. Checks portfolio-level risk.
4. Evaluates DCA conditions.
5. Evaluates ATR-based signals when technical indicators are available.
6. Optionally requests analysis from the LLM advisor.
7. Combines the available signals into a hybrid recommendation.
8. Sends approved paper trades to the simulated execution engine.
9. Logs trades and sends notifications.

### Trading Strategies

The system currently includes:

- **DCA Strategy** — makes periodic purchases when the configured price-drop condition is met.
- **ATR Strategy** — uses ATR, RSI, MACD, and volume confirmation to generate entry signals and calculate stop prices.
- **Hybrid decision layer** — combines deterministic strategy output with optional LLM analysis.

### Risk Management

The risk manager provides controls for:

- Maximum trade size
- Maximum position size
- Portfolio/global stop-loss limits
- Maximum number of active trades
- Paper-trading enforcement

The default project configuration is designed around a **$10,000 paper portfolio**, with a $500 DCA purchase amount and a 1.5× ATR multiplier. Configuration can be adjusted for experimentation.

### Market Data & Technical Analysis

The FastAPI dashboard endpoint calculates:

- RSI (14)
- MACD (12, 26, 9)
- ATR (14)
- Volume ratio relative to a 20-period average

The project uses Coinbase market data through `coinbase-advanced-py`.

### LLM Advisor

The optional LLM advisor analyzes market information such as:

- BTC price
- RSI
- MACD and signal line
- ATR
- Volume ratio

The LLM output can provide a market regime, recommendation, confidence level, reasoning, and an ATR suggestion. A confidence threshold is used before the LLM recommendation is allowed to influence the hybrid decision.

### Paper Trading

The execution engine simulates BTC purchases and sales without sending live orders to Coinbase. It tracks:

- Cash balance
- BTC holdings
- Portfolio value
- Fees
- Realized and unrealized P&L
- Trade history

### Dashboard

The React/Vite frontend communicates with the FastAPI backend and provides a visual interface for monitoring BTC price, technical indicators, portfolio information, trading mode, strategy, and system status.

## Technology Stack

**Backend / Data / AI**

- Python
- FastAPI
- Uvicorn
- Pandas
- NumPy
- Coinbase Advanced API client
- `ta` technical-analysis library
- Prophet
- OpenAI API
- ChromaDB

**Frontend**

- React
- Vite
- JavaScript / JSX
- CSS

**Development & Automation**

- Jupyter notebooks
- Git / GitHub
- GitHub Actions

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/bqsauce-ux/bitcoin-trader.git
cd bitcoin-trader
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file for credentials and API configuration.

**Never commit API keys, tokens, credentials, or other secrets to GitHub.**

Example:

```env
COINBASE_API_KEY=your_key_here
COINBASE_API_SECRET=your_secret_here
OPENAI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Use the variables required by the individual modules in your local environment.

## Running the Backend

From the repository root:

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at:

```
http://localhost:8000
```

Useful endpoints:

- `GET /` — API health message
- `GET /api/btc` — latest BTC OHLCV data
- `GET /api/dashboard` — dashboard data and technical indicators

FastAPI also provides interactive API documentation at:

```
http://localhost:8000/docs
```

## Running the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs on:

```
http://localhost:5173
```

The frontend is configured to communicate with the local FastAPI backend.

## Paper Trading Workflow

A typical paper-trading workflow is:

```
Market Data
    ↓
Technical Indicators
    ↓
DCA / ATR Strategies
    ↓
LLM Advisor (optional)
    ↓
Hybrid Decision
    ↓
Risk Manager
    ↓
Paper Trading Engine
    ↓
Trade Logger
    ↓
Notifications / Reports
```

## Research & Backtesting

The `app/` directory contains Python modules and Jupyter notebooks for experimentation, including:

- Market-data analysis
- Backtesting
- Trading-agent experiments
- Paper-trading execution
- Risk management
- Strategy metrics
- Performance metrics
- Trade logging
- LLM/ChromaDB experimentation
- Weekly reporting

These notebooks can be opened with Jupyter:

```bash
jupyter notebook
```

## Example Configuration

The project has been developed around the following paper-trading configuration:

| Parameter | Example |
|---|---:|
| Paper budget | $10,000 |
| DCA purchase | $500 |
| DCA trigger | 3% drop |
| DCA interval | 24 hours |
| ATR period | 14 |
| ATR multiplier | 1.5× |
| Maximum position | 30% |
| Maximum trade | $2,000 |
| Monitoring interval | 30 minutes |
| Trading mode | Hybrid |
| LLM advisor | Enabled |

These values are examples for the project's paper-trading setup and are not investment recommendations.

## Security

Sensitive files and credentials should remain local. The repository's `.gitignore` excludes environment files, credentials, Python cache files, virtual environments, and Node dependencies.

If a secret is accidentally committed, rotate/revoke it immediately and remove it from the repository history as appropriate.

## Future Improvements

Potential development areas include:

- More robust backtesting and walk-forward validation
- Additional trading strategies
- Improved market-regime detection
- Persistent portfolio state
- More comprehensive API endpoints
- Automated 30-minute monitoring
- Scheduled weekly email reports
- Expanded dashboard visualizations
- Improved test coverage
- Production-grade observability and error handling
- Optional live-trading integration behind explicit safety controls

## License

This project does not currently specify a license. If you plan to distribute or reuse the code, add an appropriate license file.

## Disclaimer

This software is provided for educational and research purposes only. It is not financial advice and should not be relied upon to make investment decisions. The current trading engine is intended for paper trading and does not guarantee profitability or predict future cryptocurrency prices.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.market_data import get_btc_candles

from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import AverageTrueRange

app = FastAPI(
    title="Bitcoin Trading Agent API",
    version="1.0.0",
)

# Allow the React development server to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Bitcoin Trading Agent API is running"
    }


@app.get("/api/dashboard")
def get_dashboard():
    df = get_btc_candles(days=3)

    # RSI
    rsi_indicator = RSIIndicator(
        close=df["close"],
        window=14
    )
    df["rsi"] = rsi_indicator.rsi()

    # MACD
    macd_indicator = MACD(
        close=df["close"],
        window_fast=12,
        window_slow=26,
        window_sign=9
    )

    df["macd"] = macd_indicator.macd()
    df["macdSignal"] = macd_indicator.macd_signal()

    # ATR
    atr_indicator = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    df["atr"] = atr_indicator.average_true_range()

    # Volume ratio
    df["volumeAverage"] = df["volume"].rolling(20).mean()
    df["volumeRatio"] = df["volume"] / df["volumeAverage"]

    # Remove rows where indicators haven't been calculated yet
    df = df.dropna()

    latest = df.iloc[-1]

    btc_price = float(latest["close"])

    return {
        "btcPrice": btc_price,

        "portfolioValue": 10000,
        "portfolioReturn": 0,

        "marketRegime": "unknown",
        "recommendation": "HOLD",
        "confidence": 0,

        "rsi": float(latest["rsi"]),
        "macd": float(latest["macd"]),
        "macdSignal": float(latest["macdSignal"]),
        "atr": float(latest["atr"]),
        "volumeRatio": float(latest["volumeRatio"]),

        "predicted24h": btc_price,
        "predicted7d": btc_price,
        "predicted30d": btc_price,
        "predicted1y": btc_price,
        "predicted3y": btc_price,

        "atrMultiplier": 1.5,

        "tradingMode": "Paper Trading",
        "strategy": "Hybrid",
        "monitoring": "Every 30 min",
        "llmEnabled": True,
    }

@app.get("/api/btc")
def get_btc():
    df = get_btc_candles(days=3)

    latest = df.iloc[-1]

    return {
        "timestamp": latest["timestamp"].isoformat(),
        "open": float(latest["open"]),
        "high": float(latest["high"]),
        "low": float(latest["low"]),
        "close": float(latest["close"]),
        "volume": float(latest["volume"]),
    }
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd
from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")


# ---------------------------------------------------------
# Coinbase client
# ---------------------------------------------------------

client = RESTClient(
    api_key=API_KEY,
    api_secret=API_SECRET
)


# ---------------------------------------------------------
# Get BTC historical candles
# ---------------------------------------------------------

def get_btc_candles(days=3):
    """
    Retrieve BTC-USD 30-minute candles from Coinbase.

    Parameters
    ----------
    days : int
        Number of days of historical data.

    Returns
    -------
    pandas.DataFrame
        BTC OHLCV data.
    """

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    response = client.get_candles(
        product_id="BTC-USD",
        start=int(start.timestamp()),
        end=int(end.timestamp()),
        granularity="THIRTY_MINUTE"
    )

    candles = response["candles"]

    data = []

    for candle in candles:
        data.append({
            "timestamp": pd.to_datetime(
                int(candle["start"]),
                unit="s",
                utc=True
            ),
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"]),
            "volume": float(candle["volume"])
        })

    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("No candle data returned from Coinbase.")

    df = df.sort_values("timestamp")
    df = df.reset_index(drop=True)

    return df

from prophet import Prophet
import pandas as pd


def predict_btc_prices(df, years=3):
    """
    Forecast BTC-USD prices using 30-minute historical candles.

    Parameters
    ----------
    df : pandas.DataFrame
        Historical BTC 30-minute OHLCV data.
        Must contain:
            timestamp
            open
            high
            low
            close
            volume

    years : int
        Number of years to forecast.

    Returns
    -------
    pandas.DataFrame
        Future 30-minute BTC price predictions.
    """

    # ---------------------------------------------------------
    # Prepare data for Prophet
    # ---------------------------------------------------------

    model_data = df[["timestamp", "close"]].copy()

    model_data = model_data.rename(
        columns={
            "timestamp": "ds",
            "close": "y"
        }
    )

    # Prophet works best with timezone-naive timestamps
    model_data["ds"] = (
        pd.to_datetime(model_data["ds"], utc=True)
        .dt.tz_localize(None)
    )

    # Make sure data is sorted
    model_data = model_data.sort_values("ds")

    # Remove duplicate timestamps
    model_data = model_data.drop_duplicates(
        subset=["ds"]
    )

    # Remove missing values
    model_data = model_data.dropna(
        subset=["ds", "y"]
    )

    # ---------------------------------------------------------
    # Create forecasting model
    # ---------------------------------------------------------

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )

    # ---------------------------------------------------------
    # Train model
    # ---------------------------------------------------------

    print("Training BTC forecasting model...")

    model.fit(model_data)

    # ---------------------------------------------------------
    # Calculate number of 30-minute periods
    # ---------------------------------------------------------

    periods_per_day = 48
    days_per_year = 365

    future_periods = (
        years
        * days_per_year
        * periods_per_day
    )

    print(
        f"Generating {future_periods:,} "
        f"future 30-minute predictions..."
    )

    # ---------------------------------------------------------
    # Create future 30-minute timestamps
    # ---------------------------------------------------------

    future = model.make_future_dataframe(
        periods=future_periods,
        freq="30min"
    )

    # ---------------------------------------------------------
    # Generate prediction
    # ---------------------------------------------------------

    forecast = model.predict(future)

    # ---------------------------------------------------------
    # Keep only future predictions
    # ---------------------------------------------------------

    last_historical_timestamp = model_data["ds"].max()

    forecast = forecast[
        forecast["ds"] > last_historical_timestamp
    ]

    # ---------------------------------------------------------
    # Select useful columns
    # ---------------------------------------------------------

    forecast = forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ]

    # Rename columns
    forecast = forecast.rename(
        columns={
            "ds": "timestamp",
            "yhat": "predicted_close",
            "yhat_lower": "lower_bound",
            "yhat_upper": "upper_bound"
        }
    )

    forecast = forecast.reset_index(drop=True)

    return forecast

# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    df = get_btc_candles(days=3)

    print("\nBTC Market Data")
    print("----------------")
    print(df.head())

    print("\nData shape:")
    print(df.shape)

    print("\nLatest candle:")
    print(df.tail(1))

    df.to_csv("../data/btc_candles.csv", index=False)

    print("BTC data saved successfully.")

    forecast = predict_btc_prices(
        df,
        years=3
    )

    # Save predictions
    forecast.to_csv(
        "../data/btc_3year_forecast_30min.csv",
        index=False
    )

    print(
        "\n3-year 30-minute forecast saved successfully."
    )

    print("\nFirst predictions:")
    print(forecast.head())

    print("\nLast predictions:")
    print(forecast.tail())
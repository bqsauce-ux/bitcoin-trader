from datetime import datetime
import pandas as pd


class Backtester:
    """
    Runs the Bitcoin trading system against historical
    market data.

    This version uses the existing TradingAgent in
    paper-trading mode.
    """

    def __init__(self, agent):
        self.agent = agent
        self.results = []

    # =========================================================
    # RUN BACKTEST
    # =========================================================

    def run(self, df):
        """
        Run the trading agent against historical BTC data.

        Required columns:
            price
            atr
            rsi
            macd
            macd_signal
            volume_ratio

        Optional:
            timestamp
        """

        if df.empty:
            raise ValueError(
                "Historical DataFrame is empty."
            )

        required_columns = [
            "price",
            "atr",
            "rsi",
            "macd",
            "macd_signal",
            "volume_ratio"
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        self.results = []

        for index, row in df.iterrows():

            price = float(row["price"])

            result = self.agent.process_market_data(
                price=price,
                atr=row["atr"],
                rsi=row["rsi"],
                macd=row["macd"],
                macd_signal=row["macd_signal"],
                volume_ratio=row["volume_ratio"]
            )

            portfolio = self.agent.get_portfolio()

            self.results.append({
                "index": index,
                "timestamp": row.get(
                    "timestamp",
                    datetime.now().isoformat()
                ),
                "price": price,
                "hybrid": result.get(
                    "hybrid_recommendation"
                ),
                "trade": result.get("trade"),
                "portfolio_value": portfolio.get(
                    "portfolio_value"
                ),
                "cash_usd": portfolio.get(
                    "cash_usd"
                ),
                "btc_quantity": portfolio.get(
                    "btc_quantity"
                ),
                "total_pnl": portfolio.get(
                    "total_pnl"
                ),
                "return_pct": portfolio.get(
                    "return_pct"
                )
            })

        return pd.DataFrame(self.results)

    # =========================================================
    # SUMMARY
    # =========================================================

    def summary(self):

        if not self.results:
            raise ValueError(
                "Run the backtest before requesting a summary."
            )

        df = pd.DataFrame(self.results)

        initial_value = float(
            df["portfolio_value"].iloc[0]
        )

        final_value = float(
            df["portfolio_value"].iloc[-1]
        )

        total_return_pct = (
            (final_value - initial_value)
            / initial_value
            * 100
        )

        return {
            "initial_portfolio_value": initial_value,
            "final_portfolio_value": final_value,
            "total_return_pct": total_return_pct,
            "final_pnl": float(
                df["total_pnl"].iloc[-1]
            ),
            "observations": len(df)
        }
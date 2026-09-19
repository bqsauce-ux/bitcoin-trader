from pathlib import Path
import csv
from datetime import datetime


class TradeLogger:
    """
    Records trading activity to a CSV file.

    This logger does not make trading decisions
    and does not execute trades.
    """

    HEADERS = [
        "timestamp",
        "action",
        "strategy",
        "btc_price",
        "btc_quantity",
        "usd_amount",
        "fee",
        "realized_pnl",
        "reason"
    ]

    def __init__(
        self,
        log_directory="/Users/melaniequ/bitcoin-trader/logs"
    ):
        """
        Initialize the trade logger.

        Parameters
        ----------
        log_directory : str
            Directory where trades.csv will be stored.
        """

        self.log_directory = Path(log_directory)

        # Create logs directory
        self.log_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # CSV file
        self.log_file = (
            self.log_directory / "trades.csv"
        )

        self._create_log_file()

    # =========================================================
    # CREATE LOG FILE
    # =========================================================

    def _create_log_file(self):
        """
        Create trades.csv if it does not exist.
        """

        if not self.log_file.exists():

            with open(
                self.log_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=self.HEADERS
                )

                writer.writeheader()

    # =========================================================
    # LOG TRADE
    # =========================================================

    def log_trade(self, trade):
        """
        Record a trade in trades.csv.
        """

        if not isinstance(trade, dict):
            raise TypeError(
                "trade must be a dictionary."
            )

        row = {
            "timestamp": trade.get(
                "timestamp",
                datetime.now().isoformat()
            ),

            "action": trade.get(
                "action",
                ""
            ),

            "strategy": trade.get(
                "strategy",
                ""
            ),

            "btc_price": trade.get(
                "btc_price",
                ""
            ),

            "btc_quantity": trade.get(
                "btc_quantity",
                ""
            ),

            "usd_amount": trade.get(
                "usd_amount",
                trade.get("gross_value", "")
            ),

            "fee": trade.get(
                "fee",
                ""
            ),

            "realized_pnl": trade.get(
                "realized_pnl",
                ""
            ),

            "reason": trade.get(
                "reason",
                ""
            )
        }

        with open(
            self.log_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.HEADERS
            )

            writer.writerow(row)

    # =========================================================
    # GET TRADES
    # =========================================================

    def get_trades(self):
        """
        Return all recorded trades.
        """

        if not self.log_file.exists():
            return []

        with open(
            self.log_file,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            return list(reader)

    # =========================================================
    # TRADE COUNT
    # =========================================================

    def get_trade_count(self):
        """
        Return total number of trades.
        """

        return len(self.get_trades())

    # =========================================================
    # LOG FILE LOCATION
    # =========================================================

    def get_log_path(self):
        """
        Return the path to trades.csv.
        """

        return self.log_file

    # =========================================================
    # CLEAR LOG
    # =========================================================

    def clear_log(self):
        """
        Clear the trade history.
        """

        with open(
            self.log_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.HEADERS
            )

            writer.writeheader()
from datetime import datetime


class PaperTradingEngine:
    """
    Paper trading engine for the Bitcoin trading system.

    This engine simulates:
        - BTC purchases
        - BTC sales
        - Trading fees
        - Portfolio value
        - Realized P/L
        - Unrealized P/L
        - Trade history
        - Active trades

    IMPORTANT:
        This class NEVER sends orders to Coinbase.
        It is strictly for simulation/testing.
    """

    def __init__(
        self,
        initial_cash_usd=10000,
        trading_fee_pct=0.006
    ):
        """
        Parameters
        ----------
        initial_cash_usd : float
            Starting paper-trading balance.

        trading_fee_pct : float
            Trading fee as a decimal.

            Example:
                0.006 = 0.6%
                0.001 = 0.1%
        """

        self.initial_cash_usd = float(initial_cash_usd)
        self.cash_usd = float(initial_cash_usd)

        self.btc_quantity = 0.0

        self.trading_fee_pct = float(trading_fee_pct)

        # Portfolio accounting
        self.realized_pnl = 0.0

        # Active positions
        self.active_positions = []

        # Complete trade history
        self.trade_history = []

        # Last known BTC price
        self.last_price = None

    # =========================================================
    # MARKET PRICE
    # =========================================================

    def update_price(self, btc_price):
        """
        Update the latest BTC price.
        """

        btc_price = float(btc_price)

        if btc_price <= 0:
            raise ValueError(
                "BTC price must be greater than zero."
            )

        self.last_price = btc_price

    # =========================================================
    # PORTFOLIO VALUE
    # =========================================================

    def get_btc_value(self, btc_price=None):
        """
        Calculate current BTC position value.
        """

        if btc_price is None:
            btc_price = self.last_price

        if btc_price is None:
            raise ValueError(
                "BTC price is required."
            )

        return self.btc_quantity * float(btc_price)

    def get_portfolio_value(self, btc_price=None):
        """
        Calculate total portfolio value.

        Portfolio =
            Cash + BTC value
        """

        return (
            self.cash_usd
            + self.get_btc_value(btc_price)
        )

    # =========================================================
    # BUY
    # =========================================================

    def buy_btc(
        self,
        usd_amount,
        btc_price,
        strategy="UNKNOWN",
        reason=""
    ):
        """
        Simulate a BTC purchase.

        Parameters
        ----------
        usd_amount : float
            USD amount to spend.

        btc_price : float
            BTC price.

        strategy : str
            Strategy responsible for the trade.

        reason : str
            Explanation for the trade.

        Returns
        -------
        dict
            Trade information.
        """

        usd_amount = float(usd_amount)
        btc_price = float(btc_price)

        if usd_amount <= 0:
            raise ValueError(
                "USD amount must be greater than zero."
            )

        if btc_price <= 0:
            raise ValueError(
                "BTC price must be greater than zero."
            )

        if usd_amount > self.cash_usd:
            raise ValueError(
                f"Insufficient paper cash. "
                f"Available: ${self.cash_usd:,.2f}"
            )

        # Calculate trading fee
        fee = usd_amount * self.trading_fee_pct

        # Total cash deducted
        total_cost = usd_amount + fee

        if total_cost > self.cash_usd:
            raise ValueError(
                "Insufficient cash after trading fee."
            )

        # BTC received
        btc_bought = usd_amount / btc_price

        # Update portfolio
        self.cash_usd -= total_cost
        self.btc_quantity += btc_bought

        self.last_price = btc_price

        # Record position
        position = {
            "entry_time": datetime.now().isoformat(),
            "entry_price": btc_price,
            "btc_quantity": btc_bought,
            "usd_cost": usd_amount,
            "fee": fee,
            "strategy": strategy,
            "reason": reason
        }

        self.active_positions.append(position)

        # Record trade
        trade = {
            "timestamp": datetime.now().isoformat(),
            "action": "BUY",
            "strategy": strategy,
            "btc_price": btc_price,
            "btc_quantity": btc_bought,
            "usd_amount": usd_amount,
            "fee": fee,
            "reason": reason
        }

        self.trade_history.append(trade)

        return trade

    # =========================================================
    # SELL
    # =========================================================

    def sell_btc(
        self,
        btc_quantity,
        btc_price,
        strategy="UNKNOWN",
        reason=""
    ):
        """
        Simulate selling BTC.

        FIFO accounting is used to calculate realized P/L.
        """

        btc_quantity = float(btc_quantity)
        btc_price = float(btc_price)

        if btc_quantity <= 0:
            raise ValueError(
                "BTC quantity must be greater than zero."
            )

        if btc_quantity > self.btc_quantity:
            raise ValueError(
                f"Cannot sell {btc_quantity:.8f} BTC. "
                f"Only {self.btc_quantity:.8f} BTC available."
            )

        self.last_price = btc_price

        # Gross sale value
        gross_value = btc_quantity * btc_price

        # Trading fee
        fee = gross_value * self.trading_fee_pct

        # Net amount received
        net_value = gross_value - fee

        # -----------------------------------------------------
        # Calculate realized P/L using FIFO
        # -----------------------------------------------------

        remaining_to_sell = btc_quantity
        cost_basis = 0.0

        while remaining_to_sell > 0 and self.active_positions:

            position = self.active_positions[0]

            position_btc = position["btc_quantity"]

            quantity_from_position = min(
                remaining_to_sell,
                position_btc
            )

            cost_per_btc = (
                position["usd_cost"]
                / position_btc
            )

            cost_basis += (
                quantity_from_position
                * cost_per_btc
            )

            position["btc_quantity"] -= (
                quantity_from_position
            )

            remaining_to_sell -= (
                quantity_from_position
            )

            if position["btc_quantity"] <= 0:
                self.active_positions.pop(0)

        realized_pnl = (
            net_value - cost_basis
        )

        self.realized_pnl += realized_pnl

        # Update portfolio
        self.btc_quantity -= btc_quantity
        self.cash_usd += net_value

        # Record trade
        trade = {
            "timestamp": datetime.now().isoformat(),
            "action": "SELL",
            "strategy": strategy,
            "btc_price": btc_price,
            "btc_quantity": btc_quantity,
            "gross_value": gross_value,
            "fee": fee,
            "net_value": net_value,
            "cost_basis": cost_basis,
            "realized_pnl": realized_pnl,
            "reason": reason
        }

        self.trade_history.append(trade)

        return trade

    # =========================================================
    # UNREALIZED P/L
    # =========================================================

    def get_unrealized_pnl(self, btc_price=None):
        """
        Calculate unrealized P/L on currently held BTC.

        Unrealized P/L =
            Current BTC value - estimated cost basis
        """

        if btc_price is None:
            btc_price = self.last_price

        if btc_price is None:
            raise ValueError(
                "BTC price is required."
            )

        total_cost = 0.0

        for position in self.active_positions:

            remaining_btc = position["btc_quantity"]

            if remaining_btc > 0:

                cost_per_btc = (
                    position["usd_cost"]
                    / (
                        position["btc_quantity"]
                        if position["btc_quantity"] > 0
                        else 1
                    )
                )

                total_cost += (
                    remaining_btc
                    * cost_per_btc
                )

        current_value = (
            self.btc_quantity
            * btc_price
        )

        return current_value - total_cost

    # =========================================================
    # TOTAL P/L
    # =========================================================

    def get_total_pnl(self, btc_price=None):
        """
        Calculate total portfolio P/L relative to
        the initial cash balance.
        """

        portfolio_value = self.get_portfolio_value(
            btc_price
        )

        return (
            portfolio_value
            - self.initial_cash_usd
        )

    # =========================================================
    # RETURN %
    # =========================================================

    def get_return_pct(self, btc_price=None):
        """
        Calculate portfolio return percentage.
        """

        total_pnl = self.get_total_pnl(
            btc_price
        )

        return (
            total_pnl
            / self.initial_cash_usd
        ) * 100

    # =========================================================
    # PORTFOLIO SUMMARY
    # =========================================================

    def get_portfolio_summary(self, btc_price=None):
        """
        Return complete portfolio information.
        """

        if btc_price is None:
            btc_price = self.last_price

        portfolio_value = self.get_portfolio_value(
            btc_price
        )

        total_pnl = self.get_total_pnl(
            btc_price
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "cash_usd": self.cash_usd,
            "btc_quantity": self.btc_quantity,
            "btc_price": btc_price,
            "btc_value": self.get_btc_value(
                btc_price
            ),
            "portfolio_value": portfolio_value,
            "initial_value": self.initial_cash_usd,
            "total_pnl": total_pnl,
            "return_pct": (
                total_pnl
                / self.initial_cash_usd
            ) * 100,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.get_unrealized_pnl(
                btc_price
            ),
            "active_positions": len(
                self.active_positions
            ),
            "total_trades": len(
                self.trade_history
            )
        }

    # =========================================================
    # TRADE HISTORY
    # =========================================================

    def get_trade_history(self):
        """
        Return all paper trades.
        """

        return self.trade_history

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        """
        Reset the paper trading account.
        """

        self.cash_usd = self.initial_cash_usd
        self.btc_quantity = 0.0

        self.realized_pnl = 0.0

        self.active_positions = []
        self.trade_history = []

        self.last_price = None
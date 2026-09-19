class DCAStrategy:
    """
    Dollar-Cost Averaging strategy.

    The strategy buys a fixed USD amount of BTC when:
    1. DCA is enabled
    2. The BTC price has fallen by the configured percentage
       since the previous DCA purchase
    """

    def __init__(
        self,
        buy_amount_usd=500,
        drop_pct=3.0,
        enabled=True
    ):
        self.buy_amount_usd = float(buy_amount_usd)
        self.drop_pct = float(drop_pct)
        self.enabled = enabled

        # Price at which the previous DCA purchase occurred
        self.last_buy_price = None

    def should_buy(self, current_price):
        """
        Determine whether a DCA purchase should occur.

        Returns
        -------
        dict
            Decision information.
        """

        if not self.enabled:
            return {
                "action": "HOLD",
                "reason": "DCA strategy is disabled"
            }

        current_price = float(current_price)

        # No previous purchase price
        if self.last_buy_price is None:
            return {
                "action": "BUY",
                "amount_usd": self.buy_amount_usd,
                "price": current_price,
                "reason": "Initial DCA purchase"
            }

        price_change_pct = (
            (current_price - self.last_buy_price)
            / self.last_buy_price
        ) * 100

        required_drop = -self.drop_pct

        if price_change_pct <= required_drop:

            return {
                "action": "BUY",
                "amount_usd": self.buy_amount_usd,
                "price": current_price,
                "price_change_pct": price_change_pct,
                "reason": (
                    f"BTC dropped {abs(price_change_pct):.2f}% "
                    f"since last DCA purchase"
                )
            }

        return {
            "action": "HOLD",
            "price": current_price,
            "price_change_pct": price_change_pct,
            "reason": (
                f"BTC has not dropped {self.drop_pct}% "
                "since last DCA purchase"
            )
        }

    def record_buy(self, price):
        """
        Record the price of the most recent DCA purchase.
        """

        self.last_buy_price = float(price)
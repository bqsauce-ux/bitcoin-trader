class ATRStrategy:
    """
    ATR-based strategy for active/swing trades.

    This strategy uses ATR (Average True Range) to determine
    a dynamic stop-loss level.

    Stop Loss:
        Entry Price - (ATR × multiplier)

    This class DOES NOT execute real trades.
    It only generates trading decisions and manages
    the stop-loss information for an active trade.
    """

    def __init__(
        self,
        atr_multiplier=1.5,
        enabled=True
    ):
        """
        Initialize the ATR strategy.

        Parameters
        ----------
        atr_multiplier : float
            Multiplier applied to ATR when calculating
            the stop-loss.

        enabled : bool
            Whether the ATR strategy is enabled.
        """

        self.atr_multiplier = float(atr_multiplier)
        self.enabled = enabled

        # Information about the current active trade
        self.entry_price = None
        self.entry_atr = None
        self.stop_price = None

    def calculate_stop_loss(self, entry_price, atr):
        """
        Calculate the stop-loss price.

        Formula:
            Stop = Entry Price - (ATR × multiplier)

        Parameters
        ----------
        entry_price : float
            Price at which the trade was entered.

        atr : float
            Current ATR value.

        Returns
        -------
        float
            Stop-loss price.
        """

        entry_price = float(entry_price)
        atr = float(atr)

        if entry_price <= 0:
            raise ValueError("Entry price must be greater than zero.")

        if atr < 0:
            raise ValueError("ATR cannot be negative.")

        stop_price = (
            entry_price
            - (self.atr_multiplier * atr)
        )

        return stop_price

    def generate_entry_signal(
        self,
        current_price,
        atr,
        rsi=None,
        macd=None,
        macd_signal=None,
        volume_ratio=None
    ):
        """
        Generate a potential swing-trade entry signal.

        This is intentionally conservative.

        The strategy looks for optional confirmation from:
            - RSI
            - MACD
            - Volume

        Parameters
        ----------
        current_price : float
            Current BTC price.

        atr : float
            Current ATR(14).

        rsi : float, optional
            RSI value.

        macd : float, optional
            MACD value.

        macd_signal : float, optional
            MACD signal value.

        volume_ratio : float, optional
            Current volume divided by average volume.

        Returns
        -------
        dict
            Entry decision.
        """

        current_price = float(current_price)
        atr = float(atr)

        if not self.enabled:
            return {
                "action": "HOLD",
                "price": current_price,
                "reason": "ATR strategy is disabled"
            }

        if current_price <= 0:
            raise ValueError("Current price must be greater than zero.")

        if atr <= 0:
            return {
                "action": "HOLD",
                "price": current_price,
                "reason": "Invalid or unavailable ATR"
            }

        # -------------------------------------------------
        # Confirmation conditions
        # -------------------------------------------------

        confirmations = 0
        reasons = []

        # RSI confirmation
        if rsi is not None:
            if 40 <= rsi <= 70:
                confirmations += 1
                reasons.append("RSI supports momentum")

        # MACD confirmation
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                confirmations += 1
                reasons.append("MACD bullish")

        # Volume confirmation
        if volume_ratio is not None:
            if volume_ratio >= 1.2:
                confirmations += 1
                reasons.append("volume breakout")

        # -------------------------------------------------
        # Entry rule
        #
        # Require at least two confirmations when
        # indicators are available.
        # -------------------------------------------------

        available_confirmations = sum([
            rsi is not None,
            macd is not None and macd_signal is not None,
            volume_ratio is not None
        ])

        if available_confirmations >= 2 and confirmations >= 2:

            stop_price = self.calculate_stop_loss(
                current_price,
                atr
            )

            return {
                "action": "BUY",
                "price": current_price,
                "atr": atr,
                "stop_price": stop_price,
                "atr_multiplier": self.atr_multiplier,
                "confirmations": confirmations,
                "reason": "; ".join(reasons)
            }

        return {
            "action": "HOLD",
            "price": current_price,
            "atr": atr,
            "confirmations": confirmations,
            "reason": "Insufficient bullish confirmations"
        }

    def open_trade(self, entry_price, atr):
        """
        Record an active trade.

        This does not execute a Coinbase order.
        """

        self.entry_price = float(entry_price)
        self.entry_atr = float(atr)

        self.stop_price = self.calculate_stop_loss(
            self.entry_price,
            self.entry_atr
        )

    def check_stop_loss(self, current_price):
        """
        Check whether the active trade has reached
        its stop-loss.

        Returns
        -------
        dict
            Stop-loss decision.
        """

        current_price = float(current_price)

        if self.entry_price is None:
            return {
                "action": "NO_TRADE",
                "price": current_price,
                "reason": "No active trade"
            }

        if current_price <= self.stop_price:

            loss_pct = (
                (current_price - self.entry_price)
                / self.entry_price
            ) * 100

            return {
                "action": "SELL",
                "price": current_price,
                "entry_price": self.entry_price,
                "stop_price": self.stop_price,
                "loss_pct": loss_pct,
                "reason": "ATR stop-loss triggered"
            }

        return {
            "action": "HOLD",
            "price": current_price,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,
            "reason": "Stop-loss not triggered"
        }

    def close_trade(self):
        """
        Clear the active trade information.
        """

        self.entry_price = None
        self.entry_atr = None
        self.stop_price = None
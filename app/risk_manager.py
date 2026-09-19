class RiskManager:
    """
    Portfolio-level risk management for the Bitcoin trading agent.

    The RiskManager does NOT execute trades.

    It evaluates proposed trades and determines whether
    they should be approved or rejected.

    Main protections:
        - Maximum portfolio budget
        - Maximum individual trade size
        - Maximum active position
        - Global portfolio drawdown protection
        - Maximum number of active trades
        - Paper trading mode
    """

    def __init__(
        self,
        total_budget_usd=10000,
        max_trade_usd=1000,
        max_position_usd=5000,
        global_stop_loss_pct=25.0,
        max_active_trades=3,
        paper_trading=True
    ):
        """
        Initialize the RiskManager.

        Parameters
        ----------
        total_budget_usd : float
            Maximum amount of capital allocated to the system.

        max_trade_usd : float
            Maximum USD amount allowed for one trade.

        max_position_usd : float
            Maximum total BTC position value.

        global_stop_loss_pct : float
            Maximum portfolio drawdown before all trading
            activity is paused.

        max_active_trades : int
            Maximum number of simultaneous active trades.

        paper_trading : bool
            If True, the system must not place real orders.
        """

        self.total_budget_usd = float(total_budget_usd)
        self.max_trade_usd = float(max_trade_usd)
        self.max_position_usd = float(max_position_usd)
        self.global_stop_loss_pct = float(global_stop_loss_pct)

        self.max_active_trades = int(max_active_trades)

        self.paper_trading = bool(paper_trading)

        # Track simulated/current portfolio state
        self.cash_usd = self.total_budget_usd
        self.btc_quantity = 0.0

        # Track portfolio starting value
        self.initial_portfolio_value = self.total_budget_usd

        # Number of currently active trades
        self.active_trades = 0

        # Global trading pause
        self.trading_paused = False

    # ---------------------------------------------------------
    # Portfolio calculations
    # ---------------------------------------------------------

    def get_position_value(self, btc_price):
        """
        Calculate current BTC position value.
        """

        btc_price = float(btc_price)

        return self.btc_quantity * btc_price

    def get_portfolio_value(self, btc_price):
        """
        Calculate total portfolio value.

        Portfolio =
            Cash + BTC position
        """

        return (
            self.cash_usd
            + self.get_position_value(btc_price)
        )

    def get_drawdown_pct(self, btc_price):
        """
        Calculate portfolio drawdown from initial value.
        """

        portfolio_value = self.get_portfolio_value(
            btc_price
        )

        drawdown_pct = (
            (portfolio_value - self.initial_portfolio_value)
            / self.initial_portfolio_value
        ) * 100

        return drawdown_pct

    # ---------------------------------------------------------
    # Global portfolio safeguard
    # ---------------------------------------------------------

    def check_global_stop(self, btc_price):
        """
        Check whether the portfolio has exceeded the
        maximum allowed drawdown.
        """

        drawdown_pct = self.get_drawdown_pct(btc_price)

        if drawdown_pct <= -self.global_stop_loss_pct:

            self.trading_paused = True

            return {
                "approved": False,
                "reason": (
                    f"Global portfolio stop triggered. "
                    f"Drawdown: {drawdown_pct:.2f}%"
                ),
                "drawdown_pct": drawdown_pct
            }

        return {
            "approved": True,
            "reason": "Global portfolio stop not triggered",
            "drawdown_pct": drawdown_pct
        }

    # ---------------------------------------------------------
    # Trade size validation
    # ---------------------------------------------------------

    def validate_trade_size(self, trade_amount_usd):
        """
        Check whether an individual trade is within limits.
        """

        trade_amount_usd = float(trade_amount_usd)

        if trade_amount_usd <= 0:

            return {
                "approved": False,
                "reason": "Trade amount must be greater than zero"
            }

        if trade_amount_usd > self.max_trade_usd:

            return {
                "approved": False,
                "reason": (
                    f"Trade amount ${trade_amount_usd:,.2f} "
                    f"exceeds maximum trade size "
                    f"${self.max_trade_usd:,.2f}"
                )
            }

        return {
            "approved": True,
            "reason": "Trade size is within limits"
        }

    # ---------------------------------------------------------
    # Cash validation
    # ---------------------------------------------------------

    def validate_cash(self, trade_amount_usd):
        """
        Check whether sufficient cash is available.
        """

        trade_amount_usd = float(trade_amount_usd)

        if trade_amount_usd > self.cash_usd:

            return {
                "approved": False,
                "reason": (
                    f"Insufficient cash. "
                    f"Available: ${self.cash_usd:,.2f}, "
                    f"Requested: ${trade_amount_usd:,.2f}"
                )
            }

        return {
            "approved": True,
            "reason": "Sufficient cash available"
        }

    # ---------------------------------------------------------
    # Position-size validation
    # ---------------------------------------------------------

    def validate_position_size(
        self,
        trade_amount_usd,
        btc_price
    ):
        """
        Make sure the new position won't exceed the
        maximum allowed BTC position.
        """

        current_position = self.get_position_value(
            btc_price
        )

        new_position = (
            current_position + trade_amount_usd
        )

        if new_position > self.max_position_usd:

            return {
                "approved": False,
                "reason": (
                    f"Trade would exceed maximum position. "
                    f"Current: ${current_position:,.2f}, "
                    f"New: ${new_position:,.2f}, "
                    f"Maximum: ${self.max_position_usd:,.2f}"
                )
            }

        return {
            "approved": True,
            "reason": "Position size is within limits"
        }

    # ---------------------------------------------------------
    # Active trade validation
    # ---------------------------------------------------------

    def validate_active_trades(self):
        """
        Check whether another active trade can be opened.
        """

        if self.active_trades >= self.max_active_trades:

            return {
                "approved": False,
                "reason": (
                    f"Maximum active trades reached: "
                    f"{self.max_active_trades}"
                )
            }

        return {
            "approved": True,
            "reason": "Active trade limit not reached"
        }

    # ---------------------------------------------------------
    # Complete trade validation
    # ---------------------------------------------------------

    def approve_trade(
        self,
        trade_amount_usd,
        btc_price,
        trade_type="UNKNOWN"
    ):
        """
        Perform all risk checks for a proposed trade.

        Returns
        -------
        dict
            Approval/rejection decision.
        """

        trade_amount_usd = float(trade_amount_usd)
        btc_price = float(btc_price)

        # -----------------------------------------------------
        # Check global pause
        # -----------------------------------------------------

        if self.trading_paused:

            return {
                "approved": False,
                "trade_type": trade_type,
                "reason": "Trading is globally paused"
            }

        # -----------------------------------------------------
        # Global portfolio stop
        # -----------------------------------------------------

        global_check = self.check_global_stop(
            btc_price
        )

        if not global_check["approved"]:

            return {
                "approved": False,
                "trade_type": trade_type,
                "reason": global_check["reason"]
            }

        # -----------------------------------------------------
        # Trade size
        # -----------------------------------------------------

        size_check = self.validate_trade_size(
            trade_amount_usd
        )

        if not size_check["approved"]:

            return {
                "approved": False,
                "trade_type": trade_type,
                "reason": size_check["reason"]
            }

        # -----------------------------------------------------
        # Cash
        # -----------------------------------------------------

        cash_check = self.validate_cash(
            trade_amount_usd
        )

        if not cash_check["approved"]:

            return {
                "approved": False,
                "trade_type": trade_type,
                "reason": cash_check["reason"]
            }

        # -----------------------------------------------------
        # Position
        # -----------------------------------------------------

        position_check = self.validate_position_size(
            trade_amount_usd,
            btc_price
        )

        if not position_check["approved"]:

            return {
                "approved": False,
                "trade_type": trade_type,
                "reason": position_check["reason"]
            }

        # -----------------------------------------------------
        # Active trade limit
        # -----------------------------------------------------

        if trade_type != "DCA":

            active_check = self.validate_active_trades()

            if not active_check["approved"]:

                return {
                    "approved": False,
                    "trade_type": trade_type,
                    "reason": active_check["reason"]
                }

        # -----------------------------------------------------
        # All checks passed
        # -----------------------------------------------------

        return {
            "approved": True,
            "trade_type": trade_type,
            "trade_amount_usd": trade_amount_usd,
            "btc_price": btc_price,
            "reason": "All risk checks passed"
        }

    # ---------------------------------------------------------
    # Simulate BUY
    # ---------------------------------------------------------

    def record_buy(
        self,
        trade_amount_usd,
        btc_price,
        trade_type="DCA"
    ):
        """
        Record a simulated BTC purchase.

        This method updates the internal portfolio state.
        It does NOT send an order to Coinbase.
        """

        trade_amount_usd = float(trade_amount_usd)
        btc_price = float(btc_price)

        if trade_amount_usd > self.cash_usd:

            raise ValueError(
                "Cannot record purchase: insufficient cash."
            )

        btc_bought = (
            trade_amount_usd / btc_price
        )

        self.cash_usd -= trade_amount_usd
        self.btc_quantity += btc_bought

        if trade_type != "DCA":
            self.active_trades += 1

        return {
            "trade_type": trade_type,
            "usd_spent": trade_amount_usd,
            "btc_bought": btc_bought,
            "btc_price": btc_price,
            "remaining_cash": self.cash_usd,
            "btc_quantity": self.btc_quantity
        }

    # ---------------------------------------------------------
    # Simulate SELL
    # ---------------------------------------------------------

    def record_sell(
        self,
        btc_quantity,
        btc_price,
        trade_type="SWING"
    ):
        """
        Record a simulated BTC sale.

        This method does NOT send a real Coinbase order.
        """

        btc_quantity = float(btc_quantity)
        btc_price = float(btc_price)

        if btc_quantity <= 0:

            raise ValueError(
                "BTC quantity must be greater than zero."
            )

        if btc_quantity > self.btc_quantity:

            raise ValueError(
                "Cannot sell more BTC than currently held."
            )

        usd_received = (
            btc_quantity * btc_price
        )

        self.btc_quantity -= btc_quantity
        self.cash_usd += usd_received

        if trade_type != "DCA" and self.active_trades > 0:
            self.active_trades -= 1

        return {
            "trade_type": trade_type,
            "btc_sold": btc_quantity,
            "btc_price": btc_price,
            "usd_received": usd_received,
            "remaining_cash": self.cash_usd,
            "btc_quantity": self.btc_quantity
        }

    # ---------------------------------------------------------
    # Pause / resume
    # ---------------------------------------------------------

    def pause_trading(self):
        """
        Manually pause all trading.
        """

        self.trading_paused = True

    def resume_trading(self):
        """
        Resume trading after a manual pause.
        """

        self.trading_paused = False

    # ---------------------------------------------------------
    # Portfolio summary
    # ---------------------------------------------------------

    def get_portfolio_summary(self, btc_price):
        """
        Return a summary of the current portfolio.
        """

        portfolio_value = self.get_portfolio_value(
            btc_price
        )

        drawdown_pct = self.get_drawdown_pct(
            btc_price
        )

        return {
            "cash_usd": self.cash_usd,
            "btc_quantity": self.btc_quantity,
            "btc_price": btc_price,
            "btc_position_value": self.get_position_value(
                btc_price
            ),
            "portfolio_value": portfolio_value,
            "drawdown_pct": drawdown_pct,
            "active_trades": self.active_trades,
            "trading_paused": self.trading_paused,
            "paper_trading": self.paper_trading
        }

print("risk_manager.py created successfully!")

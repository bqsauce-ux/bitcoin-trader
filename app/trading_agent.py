from datetime import datetime
from pathlib import Path
import json
import sys
from urllib.request import urlopen

# Allow the notebook-style imports below to work when this file is run as:
# python -m app.trading_agent

from .risk_manager import RiskManager
from .paper_trading_engine import PaperTradingEngine
from .trade_logger import TradeLogger

from .strategies.dca_strategy import DCAStrategy
from .strategies.atr_strategy import ATRStrategy

from .telegram_notifier import TelegramNotifier
from .llm_advisor import LLMAdvisor
from .config_loader import get_google_sheet_config, convert_config_values

class TradingAgent:
    """
    Main orchestrator for the Bitcoin trading system.

    Responsibilities:
        1. Receive market data
        2. Run trading strategies
        3. Send proposed trades to RiskManager
        4. Execute approved trades using PaperTradingEngine
        5. Record trades using TradeLogger

    IMPORTANT:
        This version is PAPER TRADING ONLY.
        It does not place real Coinbase orders.
    """

    def __init__(self, config):
        """
        Initialize the trading agent using configuration
        loaded from Google Sheets.
        """

        self.config = config

        self.risk = RiskManager(
            total_budget_usd=config["budget_usd"],
            max_trade_usd=config["max_trade_usd"],
            max_position_usd=config["max_position_usd"],
            global_stop_loss_pct=config["global_stop_loss_pct"],
            max_active_trades=config["max_active_trades"],
            paper_trading=config["paper_trading"]
        )

        self.engine = PaperTradingEngine(
            initial_cash_usd=config["budget_usd"],
            trading_fee_pct=config["trading_fee_pct"]
        )

        self.dca = DCAStrategy(
            buy_amount_usd=config["dca_buy_amount_usd"],
            drop_pct=config["dca_drop_pct"],
            enabled=config["dca_enabled"]
        )

        self.atr = ATRStrategy(
            atr_multiplier=config["atr_multiplier"],
            enabled=config["atr_enabled"]
        )

        self.logger = TradeLogger()
        self.paper_trading = config['paper_trading']
        self.telegram = TelegramNotifier()
        self.last_price = None
        self.last_signal = None

        if self.config["llm_enabled"]:
            self.llm = LLMAdvisor()
        else:
            self.llm = None

    # =========================================================
    # MARKET UPDATE
    # =========================================================

    def process_market_data(
        self,
        price,
        atr=None,
        rsi=None,
        macd=None,
        macd_signal=None,
        volume_ratio=None
    ):
        """
        Process a new market observation.

        Parameters
        ----------
        price : float
            Current BTC price.

        atr : float, optional
            ATR indicator.

        rsi : float, optional
            RSI indicator.

        macd : float, optional
            MACD value.

        macd_signal : float, optional
            MACD signal line.

        volume_ratio : float, optional
            Current volume / average volume.

        Returns
        -------
        dict
            Summary of decisions and actions.
        """

        price = float(price)

        self.last_price = price

        # Update paper engine price
        self.engine.update_price(price)

        results = {
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "dca": None,
            "atr": None,
            "trade": None
        }

        # -----------------------------------------------------
        # 1. Check global portfolio risk
        # -----------------------------------------------------

        global_risk = self.risk.check_global_stop(price)

        if not global_risk["approved"]:

            results["risk"] = global_risk

            print(
                "Trading paused:",
                global_risk["reason"]
            )

            return results

        # -----------------------------------------------------
        # 2. Run DCA strategy
        # -----------------------------------------------------

        dca_decision = self.dca.should_buy(price)

        results["dca"] = dca_decision
        atr_decision = None

        if (
            atr is not None
            and rsi is not None
            and macd is not None
            and macd_signal is not None
            and volume_ratio is not None
        ):
        
            atr_decision = self.atr.generate_entry_signal(
                current_price=price,
                atr=atr,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                volume_ratio=volume_ratio
            )
        
            results["atr"] = atr_decision
        
        
        # -----------------------------------------------------
        # 4. Run LLM analysis
        # -----------------------------------------------------
        
        llm_decision = None
        
        if (
            self.config.get("llm_enabled", False)
            and self.llm is not None
        ):
        
            llm_decision = self.llm.analyze_market(
                price=price,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                atr=atr,
                volume_ratio=volume_ratio
            )
        
            results["llm"] = llm_decision
            
        hybrid_recommendation = "HOLD"
        
        if llm_decision is not None:
        
            llm_available = llm_decision.get(
                "llm_available",
                False
            )
        
            llm_confidence = float(
                llm_decision.get(
                    "confidence",
                    0.0
                )
            )
        
            llm_recommendation = llm_decision.get(
                "recommendation",
                "HOLD"
            )
        
            min_confidence = float(
                self.config.get(
                    "llm_min_confidence",
                    0.70
                )
            )
        
            if (
                llm_available
                and llm_confidence >= min_confidence
            ):
        
                hybrid_recommendation = (
                    llm_recommendation
                )
        
            else:
        
                # LLM unavailable or not confident enough.
                # Fall back to deterministic strategies.
                hybrid_recommendation = "AUTO"
        
        else:
        
            hybrid_recommendation = "AUTO"
        
        
        results["hybrid_recommendation"] = (
            hybrid_recommendation
        )

        if (
            dca_decision.get("action") == "BUY"
            and (
                hybrid_recommendation == "DCA"
                or hybrid_recommendation == "AUTO"
            )
        ):

            trade_amount = dca_decision.get(
                "amount_usd",
                self.dca.buy_amount_usd
            )

            approval = self.risk.approve_trade(
                trade_amount_usd=trade_amount,
                btc_price=price,
                trade_type="DCA"
            )

            if approval["approved"]:

                trade = self.engine.buy_btc(
                    usd_amount=trade_amount,
                    btc_price=price,
                    strategy="DCA",
                    reason=dca_decision.get(
                        "reason",
                        "DCA buy signal"
                    )
                )

                # Tell DCA strategy that a buy occurred
                self.dca.record_buy(price)

                # Log trade
                self.logger.log_trade(trade)

                self.telegram.send_trade_notification(trade)

                results["trade"] = trade

                print(
                    f"DCA BUY executed: "
                    f"${trade_amount:,.2f} "
                    f"at ${price:,.2f}"
                )

            else:

                print(
                    "DCA trade rejected:",
                    approval["reason"]
                )

        return results

    # =========================================================
    # SELL
    # =========================================================

    def execute_sell(
        self,
        btc_quantity,
        strategy="ATR",
        reason="Stop-loss"
    ):
        """
        Execute a simulated BTC sale.

        The sale is performed through the paper trading engine.
        """

        if self.last_price is None:

            raise ValueError(
                "No current BTC price available."
            )

        if btc_quantity <= 0:

            raise ValueError(
                "BTC quantity must be greater than zero."
            )

        trade = self.engine.sell_btc(
            btc_quantity=btc_quantity,
            btc_price=self.last_price,
            strategy=strategy,
            reason=reason
        )

        self.logger.log_trade(trade)
        trade = self.engine.sell_btc(
            btc_quantity=btc_quantity,
            btc_price=self.last_price,
            strategy=strategy,
            reason=reason
        )
        
        self.logger.log_trade(trade)
        
        self.telegram.send_trade_notification(trade)
        
        return trade
        

    # =========================================================
    # PORTFOLIO
    # =========================================================

    def get_portfolio(self):
        """
        Return current portfolio summary.
        """

        return self.engine.get_portfolio_summary(
            self.last_price
        )

    # =========================================================
    # TRADE HISTORY
    # =========================================================

    def get_trade_history(self):
        """
        Return all recorded trades.
        """

        return self.logger.get_trades()

    # =========================================================
    # STATUS
    # =========================================================

    def get_status(self):
        """
        Return current system status.
        """

        return {
            "timestamp": datetime.now().isoformat(),
            "last_price": self.last_price,
            "paper_trading": self.paper_trading,
            "portfolio": self.get_portfolio(),
            "trades": len(
                self.logger.get_trades()
            )
        }


def get_current_btc_price():
    """Get the current BTC/USD spot price from Coinbase's public API."""
    with urlopen(
        "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        timeout=15,
    ) as response:
        data = json.load(response)
    return float(data["data"]["amount"])


def main():
    """Run one trading-agent cycle for GitHub Actions."""
   
    rows = get_google_sheet_config()
    config = convert_config_values(rows)
    agent = TradingAgent(config)
    price = get_current_btc_price()
    print(f"Current BTC price: ${price:,.2f}")
    result = agent.process_market_data(price=price)
    print("Trading result:")
    print(result)
    print("Portfolio status:")
    print(agent.get_status())


if __name__ == "__main__":
    main()

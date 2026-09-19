from datetime import datetime
from pathlib import Path
import sys


from .trade_logger import TradeLogger
from .trading_agent import TradingAgent
from .config_loader import get_google_sheet_config, convert_config_values


class WeeklyReport:
    """Generate a weekly performance report for the Bitcoin trading agent."""

    def __init__(self, trading_agent):
        self.agent = trading_agent
        self.logger = TradeLogger()

    def generate_report(self):
        portfolio = self.agent.get_portfolio()
        trades = self.logger.get_trades()

        total_trades = len(trades)
        buys = [trade for trade in trades if trade.get("action") == "BUY"]
        sells = [trade for trade in trades if trade.get("action") == "SELL"]

        def to_float(value):
            try:
                return float(value or 0)
            except (TypeError, ValueError):
                return 0.0

        total_fees = sum(to_float(trade.get("fee")) for trade in trades)
        total_buys = sum(to_float(trade.get("usd_amount")) for trade in buys)
        total_sells = sum(to_float(trade.get("usd_amount")) for trade in sells)

        return_pct = to_float(portfolio.get("return_pct"))
        total_pnl = to_float(portfolio.get("total_pnl"))

        report = f"""
BITCOIN TRADING AGENT
WEEKLY PERFORMANCE REPORT
========================================

Report Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PORTFOLIO
----------------------------------------
Portfolio Value:
${to_float(portfolio.get("portfolio_value")):,.2f}

Cash:
${to_float(portfolio.get("cash_usd")):,.2f}

BTC Quantity:
{to_float(portfolio.get("btc_quantity")):.8f}

BTC Price:
${to_float(portfolio.get("btc_price")):,.2f}

Total P&L:
${total_pnl:,.2f}

Return:
{return_pct:.2f}%

TRADING ACTIVITY
----------------------------------------
Total Trades:
{total_trades}

BUY Trades:
{len(buys)}

SELL Trades:
{len(sells)}

Total BUY Amount:
${total_buys:,.2f}

Total SELL Amount:
${total_sells:,.2f}

Total Fees:
${total_fees:,.2f}

SYSTEM
----------------------------------------
Paper Trading:
{self.agent.paper_trading}

Last Price:
${to_float(self.agent.last_price):,.2f}
""".strip()

        return report


def create_trading_agent():
    rows = get_google_sheet_config()
    config = convert_config_values(rows)
    return TradingAgent(config)


def main():
    agent = create_trading_agent()
    reporter = WeeklyReport(agent)
    report = reporter.generate_report()

    print(report)

    report_path = Path(__file__).resolve().parent.parent / "data" / "weekly_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report + "\n", encoding="utf-8")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()

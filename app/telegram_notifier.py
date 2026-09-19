import os
import requests
from dotenv import load_dotenv


load_dotenv()


class TelegramNotifier:
    """
    Sends trading notifications to Telegram.
    """

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is missing from .env"
            )

        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID is missing from .env"
            )

        self.base_url = (
            f"https://api.telegram.org/bot"
            f"{self.bot_token}"
        )

    def send_message(self, message):
        """
        Send a text message to Telegram.
        """

        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                f"Telegram error: {result}"
            )

        return result

    def send_trade_notification(self, trade):
        """
        Send a formatted trade notification.
        """

        action = trade.get("action", "UNKNOWN")
        strategy = trade.get("strategy", "UNKNOWN")
        price = trade.get("btc_price", 0)
        quantity = trade.get("btc_quantity", 0)
        amount = trade.get("usd_amount", 0)
        fee = trade.get("fee", 0)
        reason = trade.get("reason", "")

        if action == "BUY":
            emoji = "🟢"
        elif action == "SELL":
            emoji = "🔴"
        else:
            emoji = "ℹ️"

        message = (
            f"{emoji} BTC {action}\n\n"
            f"Strategy: {strategy}\n"
            f"Price: ${float(price):,.2f}\n"
            f"BTC: {float(quantity):.8f}\n"
            f"Amount: ${float(amount):,.2f}\n"
            f"Fee: ${float(fee):,.2f}\n"
            f"Reason: {reason}"
        )

        return self.send_message(message)


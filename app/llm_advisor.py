import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMAdvisor:
    """
    Uses an LLM to analyze Bitcoin market conditions.

    IMPORTANT:
    The LLM does NOT execute trades.

    It only provides a structured recommendation.
    The TradingAgent and RiskManager remain responsible
    for deciding whether a trade can actually happen.
    """

    def __init__(self):

        self.api_key = os.getenv("LLM_API_KEY")

        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY is missing from .env"
            )

        self.client = OpenAI(
            api_key=self.api_key
        )

        self.model = os.getenv(
            "LLM_MODEL",
            "gpt-5-mini"
        )

    # =========================================================
    # MARKET ANALYSIS
    # =========================================================

    def analyze_market(
        self,
        price,
        rsi,
        macd,
        macd_signal,
        atr,
        volume_ratio,
        sma_20=None,
        ema_20=None,
        recent_return_pct=None
    ):
        """
        Analyze the current Bitcoin market.

        Returns a structured dictionary containing:

        - market_regime
        - recommendation
        - confidence
        - reason
        - suggested_atr_multiplier
        """

        market_data = {
            "price": price,
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "atr": atr,
            "volume_ratio": volume_ratio,
            "sma_20": sma_20,
            "ema_20": ema_20,
            "recent_return_pct": recent_return_pct
        }

        prompt = f"""
You are a Bitcoin trading market-analysis assistant.

Analyze the following technical market data.

Market data:
{json.dumps(market_data, indent=2)}

Determine:

1. Market regime:
   - bullish
   - bearish
   - sideways
   - high_volatility

2. Recommended strategy:
   - DCA
   - SWING
   - HOLD

3. Confidence from 0 to 1.

4. A short explanation.

5. A reasonable ATR stop-loss multiplier between
   1.0 and 3.0.

IMPORTANT:
You are only providing analysis.
You are NOT executing a trade.

Return ONLY valid JSON in exactly this format:

{{
    "market_regime": "bullish",
    "recommendation": "SWING",
    "confidence": 0.75,
    "reason": "Short explanation",
    "suggested_atr_multiplier": 1.5
}}
"""
        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        text = response.output_text.strip()

        try:
            result = json.loads(text)

        except json.JSONDecodeError as exc:

            raise ValueError(
                f"LLM returned invalid JSON: {text}"
            ) from exc

        return self._validate_result(result)

    # =========================================================
    # VALIDATE RESPONSE
    # =========================================================

    def _validate_result(self, result):
        """
        Validate and sanitize the LLM response.
        """

        required_fields = [
            "market_regime",
            "recommendation",
            "confidence",
            "reason",
            "suggested_atr_multiplier"
        ]

        for field in required_fields:

            if field not in result:
                raise ValueError(
                    f"LLM response missing: {field}"
                )

        valid_regimes = {
            "bullish",
            "bearish",
            "sideways",
            "high_volatility"
        }

        valid_recommendations = {
            "DCA",
            "SWING",
            "HOLD"
        }

        regime = result["market_regime"].lower()

        recommendation = (
            result["recommendation"].upper()
        )

        if regime not in valid_regimes:
            raise ValueError(
                f"Invalid market regime: {regime}"
            )

        if recommendation not in valid_recommendations:
            raise ValueError(
                f"Invalid recommendation: "
                f"{recommendation}"
            )

        confidence = float(
            result["confidence"]
        )

        confidence = max(
            0.0,
            min(1.0, confidence)
        )

        atr_multiplier = float(
            result["suggested_atr_multiplier"]
        )

        # Never allow the LLM to suggest an
        # extreme stop-loss multiplier.
        atr_multiplier = max(
            1.0,
            min(3.0, atr_multiplier)
        )

        return {
            "market_regime": regime,
            "recommendation": recommendation,
            "confidence": confidence,
            "reason": str(result["reason"]),
            "suggested_atr_multiplier": atr_multiplier
        }
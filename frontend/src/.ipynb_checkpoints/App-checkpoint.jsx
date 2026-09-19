import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function App() {
  const [market, setMarket] = useState(null);
  const [error, setError] = useState(null);

  // Get dashboard data from FastAPI
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/dashboard")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Dashboard data:", data);
        setMarket(data);
      })
      .catch((error) => {
        console.error("Failed to load dashboard:", error);
        setError(error.message);
      });
  }, []);

  // Loading state
  if (!market && !error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">
          <div className="text-2xl font-bold">
            Bitcoin Trading Agent
          </div>
          <p className="mt-2 text-slate-400">
            Connecting to FastAPI...
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <Card className="w-full max-w-lg border-red-900 bg-slate-900">
          <CardHeader>
            <CardTitle className="text-red-400">
              Backend Connection Error
            </CardTitle>
          </CardHeader>

          <CardContent>
            <p className="text-slate-300">
              Could not connect to FastAPI.
            </p>

            <p className="mt-3 rounded bg-slate-950 p-3 font-mono text-sm text-red-300">
              {error}
            </p>

            <p className="mt-4 text-sm text-slate-400">
              Make sure FastAPI is running on port 8000.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold">
              Bitcoin Trading Agent
            </h1>

            <p className="text-sm text-slate-400">
              AI-powered autonomous trading system
            </p>
          </div>

          <Badge className="bg-green-600">
            ● System Online
          </Badge>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-6">

        {/* Top Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

          <Card className="border-slate-800 bg-slate-900">
            <CardHeader>
              <CardTitle className="text-sm text-slate-400">
                BTC Price
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="text-3xl font-bold">
                ${market.btcPrice.toLocaleString()}
              </div>

              <p className="mt-1 text-sm text-green-400">
                +3.2% recent return
              </p>
            </CardContent>
          </Card>


          <Card className="border-slate-800 bg-slate-900">
            <CardHeader>
              <CardTitle className="text-sm text-slate-400">
                Portfolio
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="text-3xl font-bold">
                ${market.portfolioValue.toLocaleString()}
              </div>

              <p className="mt-1 text-sm text-green-400">
                +{market.portfolioReturn}%
              </p>
            </CardContent>
          </Card>


          <Card className="border-slate-800 bg-slate-900">
            <CardHeader>
              <CardTitle className="text-sm text-slate-400">
                Market Regime
              </CardTitle>
            </CardHeader>

            <CardContent>
              <Badge className="bg-green-600 text-base">
                {market.marketRegime.toUpperCase()}
              </Badge>
            </CardContent>
          </Card>


          <Card className="border-slate-800 bg-slate-900">
            <CardHeader>
              <CardTitle className="text-sm text-slate-400">
                AI Recommendation
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="text-3xl font-bold">
                {market.recommendation}
              </div>

              <p className="mt-1 text-sm text-slate-400 text-white">
                Confidence:{" "}
                {(market.confidence * 100).toFixed(0)}%
              </p>
            </CardContent>
          </Card>

        </div>


        {/* Technical Indicators */}
        <Card className="border-slate-800 bg-slate-900 text-white">
          <CardHeader>
            <CardTitle>
              Technical Indicators
            </CardTitle>
          </CardHeader>

          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5 text-white">

              <Indicator
                name="RSI"
                value={market.rsi}
              />

              <Indicator
                name="MACD"
                value={market.macd}
              />

              <Indicator
                name="MACD Signal"
                value={market.macdSignal}
              />

              <Indicator
                name="ATR"
                value={market.atr}
              />

              <Indicator
                name="Volume Ratio"
                value={`${market.volumeRatio}x`}
              />

            </div>
          </CardContent>
        </Card>


        {/* Forecast */}
        <Card className="border-slate-800 bg-slate-900 text-white">
          <CardHeader>
            <CardTitle>
              AI Price Forecast
            </CardTitle>

            <p className="text-sm text-slate-400 text-white">
              Model-generated BTC price projections
            </p>
          </CardHeader>

          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5 text-white">

              <Forecast
                horizon="24 Hours"
                price={market.predicted24h}
              />

              <Forecast
                horizon="7 Days"
                price={market.predicted7d}
              />

              <Forecast
                horizon="30 Days"
                price={market.predicted30d}
              />

              <Forecast
                horizon="1 Year"
                price={market.predicted1y}
              />

              <Forecast
                horizon="3 Years"
                price={market.predicted3y}
              />

            </div>
          </CardContent>
        </Card>


        {/* AI + Risk */}
        <div className="grid gap-6 lg:grid-cols-2 text-white">

          {/* LLM Analysis */}
          <Card className="border-slate-800 bg-slate-900 text-white">
            <CardHeader>
              <CardTitle>
                LLM Market Analysis
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">

              <div>
                <p className="text-sm text-slate-400 text-white">
                  Recommendation
                </p>

                <p className="text-2xl font-bold">
                  {market.recommendation}
                </p>
              </div>


              <div>
                <p className="text-sm text-slate-400 text-white">
                  Confidence
                </p>

                <div className="mt-2 h-3 rounded-full bg-slate-700 text-white">
                  <div
                    className="h-3 rounded-full bg-green-500"
                    style={{
                      width: `${market.confidence * 100}%`,
                    }}
                  />
                </div>

                <p className="mt-1 text-sm">
                  {(market.confidence * 100).toFixed(0)}%
                </p>
              </div>


              <div>
                <p className="text-sm text-slate-400 text-white">
                  Reason
                </p>

                <p className="mt-1 text-slate-200 text-white">
                  Technical indicators show bullish momentum
                  with elevated volume. The model favors a
                  swing strategy while maintaining ATR-based
                  risk protection.
                </p>
              </div>

            </CardContent>
          </Card>


          {/* Risk Management */}
          <Card className="border-slate-800 bg-slate-900 text-white">
            <CardHeader>
              <CardTitle>
                Risk Management
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">

              <RiskRow
                label="ATR Multiplier"
                value={`${market.atrMultiplier}x`}
              />

              <RiskRow
                label="ATR Stop Distance"
                value={`$${(
                  market.atr * market.atrMultiplier
                ).toLocaleString()}`}
              />

              <RiskRow
                label="Portfolio Stop"
                value="25%"
              />

              <RiskRow
                label="Max Position"
                value="30%"
              />

              <RiskRow
                label="DCA Amount"
                value="$500"
              />

              <RiskRow
                label="DCA Trigger"
                value="3%"
              />

            </CardContent>
          </Card>

        </div>


        {/* Trading Status */}
        <Card className="border-slate-800 bg-slate-900 text-white">
          <CardHeader>
            <CardTitle>
              Trading Agent Status
            </CardTitle>
          </CardHeader>

          <CardContent>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 text-white">

              <Status
                label="Trading Mode"
                value={market.tradingMode}
              />

              <Status
                label="Strategy"
                value={market.strategy}
              />

              <Status
                label="Monitoring"
                value={market.monitoring}
              />

              <Status
                label="LLM"
                value={market.llmEnabled ? "Enabled" : "Disabled"}
              />

            </div>

          </CardContent>
        </Card>


        {/* Recent Activity */}
        <Card className="border-slate-800 bg-slate-900 text-white">
          <CardHeader>
            <CardTitle>
              Recent Activity
            </CardTitle>
          </CardHeader>

          <CardContent>

            <div className="space-y-3">

              <Activity
                time="12:00 PM"
                message="LLM analyzed BTC market"
                status="Analysis"
              />

              <Activity
                time="11:30 AM"
                message={`ATR calculated: ${market.atr.toLocaleString()}`}
                status="Risk"
              />

              <Activity
                time="11:00 AM"
                message={`BTC price updated: $${market.btcPrice.toLocaleString()}`}
                status="Market"
              />

              <Activity
                time="10:30 AM"
                message="No trade executed"
                status="Hold"
              />

            </div>

          </CardContent>
        </Card>

      </main>
    </div>
  );
}


/* ================================
   Reusable Components
================================ */

function Indicator({ name, value }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">
        {name}
      </p>

      <p className="mt-2 text-xl font-semibold">
        {value}
      </p>
    </div>
  );
}


function Forecast({ horizon, price }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">
        {horizon}
      </p>

      <p className="mt-2 text-xl font-semibold">
        ${price.toLocaleString()}
      </p>
    </div>
  );
}


function RiskRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800 pb-3">
      <span className="text-slate-400">
        {label}
      </span>

      <span className="font-semibold">
        {value}
      </span>
    </div>
  );
}


function Status({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">
        {label}
      </p>

      <p className="mt-2 font-semibold">
        {value}
      </p>
    </div>
  );
}


function Activity({ time, message, status }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800 pb-3">

      <div>
        <p className="font-medium">
          {message}
        </p>

        <p className="text-sm text-slate-500">
          {time}
        </p>
      </div>

      <Badge variant="secondary">
        {status}
      </Badge>

    </div>
  );
}


export default App;

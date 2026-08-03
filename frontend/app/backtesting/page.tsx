"use client";

import { useState } from "react";
import { Play, AlertTriangle } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input, Select, Label } from "../components/ui/Input";
import { Skeleton } from "../components/ui/Skeleton";
import { EquityCurveChart } from "../components/ui/EquityCurveChart";

interface BacktestResult {
  symbol: string;
  strategy: string;
  total_return_pct: number;
  annualized_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  trades: number;
  win_rate_pct: number;
  equity_curve: number[];
  dates: string[];
}

const strategies = [
  { value: "buy_hold", label: "Buy & Hold" },
  { value: "sma_crossover", label: "SMA Crossover (20/50)" },
  { value: "rsi_mean_reversion", label: "RSI Mean Reversion (14)" },
  { value: "macd", label: "MACD Signal (12/26/9)" },
];

export default function Backtesting() {
  const [symbol, setSymbol] = useState("AAPL");
  const [strategy, setStrategy] = useState("buy_hold");
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runBacktest = async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/backtest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, strategy, start_date: startDate, end_date: endDate }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch {
      setError("Couldn't reach the backend. Confirm it's running and reachable.");
    } finally {
      setLoading(false);
    }
  };

  const stats = result
    ? [
        { label: "Total return", value: `${result.total_return_pct >= 0 ? "+" : ""}${result.total_return_pct.toFixed(2)}%`, tone: result.total_return_pct >= 0 ? "gain" : "loss" },
        { label: "Annualized return", value: `${result.annualized_return_pct >= 0 ? "+" : ""}${result.annualized_return_pct.toFixed(2)}%`, tone: result.annualized_return_pct >= 0 ? "gain" : "loss" },
        { label: "Max drawdown", value: `${result.max_drawdown_pct.toFixed(2)}%`, tone: "loss" },
        { label: "Sharpe ratio", value: result.sharpe_ratio.toFixed(2), tone: "signal" },
        { label: "Total trades", value: String(result.trades), tone: "ink" },
        { label: "Win rate", value: `${result.win_rate_pct.toFixed(0)}%`, tone: "gain" },
      ]
    : [];

  const toneClass: Record<string, string> = {
    gain: "text-gain",
    loss: "text-loss",
    signal: "text-signal",
    ink: "text-ink",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">Backtesting</h1>
        <p className="text-sm text-ink-muted mt-1">
          Simulates a strategy against real historical daily closes, long/flat only, no transaction costs modeled.
        </p>
      </div>

      <Card>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Label>Symbol</Label>
            <Input mono value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="w-full" />
          </div>
          <div>
            <Label>Strategy</Label>
            <Select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="w-full">
              {strategies.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Start date</Label>
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full" />
          </div>
          <div>
            <Label>End date</Label>
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full" />
          </div>
        </div>
        <Button onClick={runBacktest} disabled={loading} className="mt-4">
          <Play className="w-4 h-4" /> {loading ? "Running…" : "Run backtest"}
        </Button>
      </Card>

      {error && (
        <Card className="border-loss/30 bg-loss-soft text-loss text-sm flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" /> {error}
        </Card>
      )}

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <Skeleton className="h-3 w-20 mb-2" />
              <Skeleton className="h-7 w-24" />
            </Card>
          ))}
        </div>
      )}

      {result && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stats.map((s) => (
              <Card key={s.label}>
                <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-1.5">{s.label}</p>
                <p className={`font-mono text-2xl font-semibold tabular-nums ${toneClass[s.tone]}`}>{s.value}</p>
              </Card>
            ))}
          </div>

          <Card>
            <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-3">
              Equity curve · {result.symbol} · {strategies.find((s) => s.value === result.strategy)?.label}
            </p>
            <EquityCurveChart equity={result.equity_curve} dates={result.dates} />
          </Card>
        </>
      )}

      <Card className="bg-signal-soft border-signal/20 text-sm text-signal">
        Historical closes come from Yahoo Finance. Results assume no transaction costs or slippage and never short
        the market — a production backtester would need both, plus walk-forward validation, to be decision-grade.
      </Card>
    </div>
  );
}

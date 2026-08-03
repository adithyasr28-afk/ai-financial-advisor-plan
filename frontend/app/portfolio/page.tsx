"use client";

import { useState, useEffect } from "react";
import { Plus, X, Briefcase } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Sparkline } from "../components/ui/Sparkline";
import { EmptyState } from "../components/ui/EmptyState";

interface MarketData {
  symbol: string;
  price: number;
  change_pct: number;
  bars: Array<{ close: number; date: string | null }>;
}

interface Holding {
  symbol: string;
  shares: number;
  avg_cost: number;
}

function money(n: number) {
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default function Portfolio() {
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [holdings, setHoldings] = useState<Holding[]>([
    { symbol: "AAPL", shares: 10, avg_cost: 150 },
    { symbol: "MSFT", shares: 5, avg_cost: 300 },
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchMarketData() {
      setLoading(true);
      try {
        const symbols = [...new Set(holdings.map((h) => h.symbol).filter(Boolean))];
        const results = await Promise.all(
          symbols.map((sym) =>
            fetch(`${API_BASE_URL}/api/v1/market-data/${sym}`).then((r) => (r.ok ? r.json() : null))
          )
        );
        const data: Record<string, MarketData> = {};
        results.forEach((d) => {
          if (d && d.symbol) data[d.symbol] = d;
        });
        setMarketData(data);
      } catch {
        // network hiccup - table just falls back to cost basis below
      } finally {
        setLoading(false);
      }
    }
    fetchMarketData();
  }, [holdings]);

  const totalValue = holdings.reduce((sum, h) => sum + (marketData[h.symbol]?.price ?? h.avg_cost) * h.shares, 0);
  const totalCost = holdings.reduce((sum, h) => sum + h.avg_cost * h.shares, 0);
  const totalPnl = totalValue - totalCost;
  const totalPnlPct = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;

  const addHolding = () => setHoldings([...holdings, { symbol: "", shares: 0, avg_cost: 0 }]);
  const removeHolding = (idx: number) => setHoldings(holdings.filter((_, i) => i !== idx));
  const updateHolding = (idx: number, field: keyof Holding, value: string | number) => {
    setHoldings(
      holdings.map((h, i) =>
        i === idx ? { ...h, [field]: typeof value === "string" ? value.toUpperCase() : value } : h
      )
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">Portfolio</h1>
        <p className="text-sm text-ink-muted mt-1">Holdings marked to the latest available price.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-1.5">Market value</p>
          <p className="font-mono text-2xl font-semibold text-ink tabular-nums">${money(totalValue)}</p>
        </Card>
        <Card>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-1.5">Cost basis</p>
          <p className="font-mono text-2xl font-semibold text-ink tabular-nums">${money(totalCost)}</p>
        </Card>
        <Card>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-1.5">Unrealized P&L</p>
          <p className={`font-mono text-2xl font-semibold tabular-nums ${totalPnl >= 0 ? "text-gain" : "text-loss"}`}>
            {totalPnl >= 0 ? "+" : ""}
            ${money(totalPnl)}{" "}
            <span className="text-sm font-medium">
              ({totalPnlPct >= 0 ? "+" : ""}
              {totalPnlPct.toFixed(2)}%)
            </span>
          </p>
        </Card>
      </div>

      <Card padded={false} className="overflow-hidden">
        {holdings.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title="No holdings yet"
            description="Add a symbol below to start tracking market value and P&L."
          />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs font-medium uppercase tracking-wide text-ink-faint">
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Shares</th>
                <th className="px-4 py-3 font-medium">Avg cost</th>
                <th className="px-4 py-3 font-medium">Price</th>
                <th className="px-4 py-3 font-medium">Trend</th>
                <th className="px-4 py-3 font-medium">Value</th>
                <th className="px-4 py-3 font-medium">P&L</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {holdings.map((holding, idx) => {
                const md = marketData[holding.symbol];
                const price = md?.price ?? holding.avg_cost;
                const marketValue = price * holding.shares;
                const cost = holding.avg_cost * holding.shares;
                const pnl = marketValue - cost;
                const pnlPct = cost > 0 ? (pnl / cost) * 100 : 0;

                return (
                  <tr key={idx} className="hover:bg-paper transition-colors">
                    <td className="px-4 py-2.5">
                      <input
                        value={holding.symbol}
                        onChange={(e) => updateHolding(idx, "symbol", e.target.value)}
                        className="w-20 bg-transparent font-mono font-medium text-ink uppercase outline-none focus:text-signal"
                      />
                    </td>
                    <td className="px-4 py-2.5">
                      <input
                        type="number"
                        value={holding.shares}
                        onChange={(e) => updateHolding(idx, "shares", Number(e.target.value))}
                        className="w-20 bg-transparent font-mono text-ink outline-none focus:text-signal"
                        min="0"
                        step="0.01"
                      />
                    </td>
                    <td className="px-4 py-2.5">
                      <input
                        type="number"
                        value={holding.avg_cost}
                        onChange={(e) => updateHolding(idx, "avg_cost", Number(e.target.value))}
                        className="w-24 bg-transparent font-mono text-ink outline-none focus:text-signal"
                        min="0"
                        step="0.01"
                      />
                    </td>
                    <td className="px-4 py-2.5 font-mono text-ink tabular-nums">
                      {md ? `$${price.toFixed(2)}` : "—"}
                    </td>
                    <td className="px-4 py-2.5">
                      <Sparkline values={md?.bars.map((b) => b.close) ?? []} width={64} height={22} />
                    </td>
                    <td className="px-4 py-2.5 font-mono text-ink tabular-nums">${money(marketValue)}</td>
                    <td className="px-4 py-2.5 font-mono tabular-nums">
                      <span className={pnl >= 0 ? "text-gain" : "text-loss"}>
                        {pnl >= 0 ? "+" : ""}
                        {pnlPct.toFixed(2)}%
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <button
                        onClick={() => removeHolding(idx)}
                        disabled={holdings.length <= 1}
                        className="text-ink-faint hover:text-loss disabled:opacity-30 transition-colors"
                        aria-label={`Remove ${holding.symbol || "holding"}`}
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </Card>

      <div className="flex items-center gap-3">
        <Button variant="secondary" onClick={addHolding}>
          <Plus className="w-4 h-4" /> Add holding
        </Button>
        {loading && <span className="text-xs text-ink-faint">Refreshing prices…</span>}
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { Plus, X, Eye } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";

interface MarketData {
  symbol: string;
  price: number;
  change_pct: number;
}

interface WatchlistItem {
  symbol: string;
  name?: string;
}

export default function Watchlists() {
  const [watchlists, setWatchlists] = useState<Record<string, WatchlistItem[]>>({
    "My Watchlist": [{ symbol: "AAPL" }, { symbol: "MSFT" }, { symbol: "GOOGL" }],
    "Tech Giants": [{ symbol: "NVDA" }, { symbol: "META" }, { symbol: "AMZN" }],
  });
  const [activeList, setActiveList] = useState("My Watchlist");
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [loading, setLoading] = useState(false);
  const [newSymbol, setNewSymbol] = useState("");
  const [newListName, setNewListName] = useState("");

  useEffect(() => {
    async function fetchMarketData() {
      setLoading(true);
      try {
        const symbols = [...new Set(watchlists[activeList]?.map((w) => w.symbol) || [])];
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
        // ignore - row falls back to a placeholder price
      } finally {
        setLoading(false);
      }
    }
    fetchMarketData();
  }, [watchlists, activeList]);

  const addSymbol = () => {
    if (!newSymbol.trim()) return;
    setWatchlists((prev) => ({
      ...prev,
      [activeList]: [...(prev[activeList] || []), { symbol: newSymbol.toUpperCase() }],
    }));
    setNewSymbol("");
  };

  const removeSymbol = (symbol: string) => {
    setWatchlists((prev) => ({
      ...prev,
      [activeList]: (prev[activeList] || []).filter((w) => w.symbol !== symbol),
    }));
  };

  const createList = () => {
    if (!newListName.trim()) return;
    setWatchlists((prev) => ({ ...prev, [newListName]: [] }));
    setActiveList(newListName);
    setNewListName("");
  };

  const currentList = watchlists[activeList] || [];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Watchlists</h1>
          <p className="text-sm text-ink-muted mt-1">Group symbols and track them at a glance.</p>
        </div>
        <div className="flex gap-2">
          <Input
            value={newListName}
            onChange={(e) => setNewListName(e.target.value)}
            placeholder="New watchlist name"
            className="w-48"
            onKeyDown={(e) => e.key === "Enter" && createList()}
          />
          <Button variant="secondary" onClick={createList}>
            <Plus className="w-4 h-4" /> Create
          </Button>
        </div>
      </div>

      <div className="flex gap-1.5 border-b border-line">
        {Object.keys(watchlists).map((name) => (
          <button
            key={name}
            onClick={() => setActiveList(name)}
            className={`px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              activeList === name
                ? "border-signal text-signal"
                : "border-transparent text-ink-muted hover:text-ink"
            }`}
          >
            {name}
          </button>
        ))}
      </div>

      <Card padded={false}>
        <div className="p-4 border-b border-line flex gap-2 items-center">
          <Input
            mono
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
            placeholder="Add symbol, e.g. TSLA"
            className="w-48"
            onKeyDown={(e) => e.key === "Enter" && addSymbol()}
          />
          <Button onClick={addSymbol}>
            <Plus className="w-4 h-4" /> Add
          </Button>
          {loading && <span className="text-xs text-ink-faint ml-2">Refreshing…</span>}
        </div>

        {currentList.length === 0 ? (
          <EmptyState
            icon={Eye}
            title="This watchlist is empty"
            description="Add a symbol above to start tracking it here."
          />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium uppercase tracking-wide text-ink-faint">
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Price</th>
                <th className="px-4 py-3 font-medium">Change</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {currentList.map((item) => {
                const data = marketData[item.symbol];
                return (
                  <tr key={item.symbol} className="hover:bg-paper transition-colors">
                    <td className="px-4 py-2.5 font-mono font-medium text-ink">{item.symbol}</td>
                    <td className="px-4 py-2.5 font-mono text-ink tabular-nums">
                      {data ? `$${data.price.toFixed(2)}` : "—"}
                    </td>
                    <td className="px-4 py-2.5 font-mono tabular-nums">
                      {data && (
                        <span className={data.change_pct >= 0 ? "text-gain" : "text-loss"}>
                          {data.change_pct >= 0 ? "+" : ""}
                          {data.change_pct.toFixed(2)}%
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <button
                        onClick={() => removeSymbol(item.symbol)}
                        className="text-ink-faint hover:text-loss transition-colors"
                        aria-label={`Remove ${item.symbol}`}
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
    </div>
  );
}

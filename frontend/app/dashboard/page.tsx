"use client";

import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Newspaper } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card, CardHeader } from "../components/ui/Card";
import { Sparkline } from "../components/ui/Sparkline";
import { Skeleton, SkeletonLine } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";

interface MarketData {
  symbol: string;
  price: number;
  change_pct: number;
  bars: Array<{ close: number; date: string | null }>;
  live?: boolean;
}

interface NewsArticle {
  title: string;
  link: string;
  source: string;
  published: string | null;
}

interface MacroData {
  series_id: string;
  value: number;
  observation_date: string;
  source: string;
  live?: boolean;
}

function LiveBadge({ live }: { live?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-medium uppercase tracking-wide ${live ? "text-gain" : "text-ink-faint"}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${live ? "bg-gain" : "bg-ink-faint"}`} />
      {live ? "Live" : "Cached"}
    </span>
  );
}

export default function Dashboard() {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [macro, setMacro] = useState<MacroData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [marketRes, newsRes, macroRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/market-data/AAPL`),
          fetch(`${API_BASE_URL}/api/v1/news?limit=5`),
          fetch(`${API_BASE_URL}/api/v1/macro/GDP`),
        ]);

        if (marketRes.ok) setMarketData(await marketRes.json());
        if (newsRes.ok) {
          const data = await newsRes.json();
          setNews(data.articles);
        }
        if (macroRes.ok) setMacro(await macroRes.json());
      } catch {
        setError("Couldn't reach the backend. Confirm it's running and NEXT_PUBLIC_API_URL is set correctly.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">Dashboard</h1>
        <p className="text-sm text-ink-muted mt-1">Market snapshot, macro read, and today's headlines.</p>
      </div>

      {error && (
        <Card className="border-loss/30 bg-loss-soft text-loss text-sm">{error}</Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader eyebrow="Equity" title="AAPL" action={marketData && !loading ? <LiveBadge live={marketData.live} /> : undefined} />
          {loading ? (
            <div className="space-y-3">
              <SkeletonLine width="60%" />
              <Skeleton className="h-8 w-full" />
            </div>
          ) : marketData && !("error" in marketData) ? (
            <div>
              <div className="flex items-end justify-between">
                <div className="font-mono text-3xl font-semibold text-ink tabular-nums">
                  ${marketData.price.toFixed(2)}
                </div>
                <Sparkline values={marketData.bars.map((b) => b.close)} width={90} height={30} />
              </div>
              <div
                className={`flex items-center gap-1 mt-2 text-sm font-mono ${
                  marketData.change_pct >= 0 ? "text-gain" : "text-loss"
                }`}
              >
                {marketData.change_pct >= 0 ? (
                  <TrendingUp className="w-3.5 h-3.5" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5" />
                )}
                {marketData.change_pct >= 0 ? "+" : ""}
                {marketData.change_pct.toFixed(2)}%
              </div>
            </div>
          ) : (
            <p className="text-sm text-ink-faint">No fixture data for this symbol yet.</p>
          )}
        </Card>

        <Card>
          <CardHeader eyebrow="Macro" title={macro?.series_id ?? "Indicator"} action={macro && !loading ? <LiveBadge live={macro.live} /> : undefined} />
          {loading ? (
            <div className="space-y-3">
              <SkeletonLine width="50%" />
              <SkeletonLine width="70%" />
            </div>
          ) : macro ? (
            <div>
              <div className="font-mono text-3xl font-semibold text-ink tabular-nums">
                {macro.value.toLocaleString()}
              </div>
              <p className="text-sm text-ink-muted mt-2">As of {macro.observation_date}</p>
              <p className="text-xs text-ink-faint mt-1">Source: {macro.source}</p>
            </div>
          ) : (
            <p className="text-sm text-ink-faint">No macro reading available.</p>
          )}
        </Card>

        <Card className="md:col-span-1 md:row-span-1">
          <CardHeader eyebrow="Coverage" title="Agents online" />
          <div className="font-mono text-3xl font-semibold text-ink">8 / 8</div>
          <p className="text-sm text-ink-muted mt-2">
            News, valuation, risk, technicals, portfolio, macro, fundamentals, report writer.
          </p>
        </Card>
      </div>

      <Card>
        <CardHeader eyebrow="Latest" title="Financial news" />
        {loading ? (
          <div className="space-y-4">
            {[0, 1, 2].map((i) => (
              <div key={i} className="space-y-2">
                <SkeletonLine width="80%" />
                <SkeletonLine width="30%" />
              </div>
            ))}
          </div>
        ) : news.length > 0 ? (
          <div className="divide-y divide-line">
            {news.slice(0, 5).map((article, idx) => (
              <a
                key={idx}
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-3 py-3 first:pt-0 last:pb-0 hover:bg-paper -mx-2 px-2 rounded transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-sm text-ink truncate">{article.title}</p>
                  <p className="text-xs text-ink-faint mt-1">{article.source}</p>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <EmptyState icon={Newspaper} title="No headlines yet" description="Check back once the news feed has ingested articles." />
        )}
      </Card>
    </div>
  );
}

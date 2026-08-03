"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Building2,
  Briefcase,
  Newspaper,
  Eye,
  MessagesSquare,
  Bell,
  FlaskConical,
  ArrowUpRight,
} from "lucide-react";
import { ConsensusStrip } from "./components/ui/ConsensusStrip";

const pages = [
  { href: "/dashboard", title: "Dashboard", description: "Market overview, news, and macro indicators", icon: LayoutDashboard },
  { href: "/company", title: "Company Analysis", description: "Eight specialist agents, one evidence trail", icon: Building2 },
  { href: "/portfolio", title: "Portfolio", description: "Track holdings, P&L, and market values", icon: Briefcase },
  { href: "/news", title: "News", description: "Real-time financial news feed", icon: Newspaper },
  { href: "/watchlists", title: "Watchlists", description: "Create and monitor custom watchlists", icon: Eye },
  { href: "/chat", title: "AI Chat", description: "Ask a question, agents debate the answer", icon: MessagesSquare },
  { href: "/alerts", title: "Alerts", description: "Price and percentage change notifications", icon: Bell },
  { href: "/backtesting", title: "Backtesting", description: "Strategy simulation and performance metrics", icon: FlaskConical },
];

const sampleConsensus = [
  { agent: "valuation", stance: "bullish", confidence: 0.78 },
  { agent: "technical_analysis", stance: "bullish", confidence: 0.61 },
  { agent: "risk", stance: "hold", confidence: 0.55 },
  { agent: "news_intelligence", stance: "bullish", confidence: 0.44 },
  { agent: "macro_economy", stance: "hold", confidence: 0.5 },
  { agent: "portfolio", stance: "hold", confidence: 0.4 },
  { agent: "financial_statement", stance: "bearish", confidence: 0.52 },
  { agent: "report_writer", stance: "conflict", confidence: 0.6 },
];

export default function Home() {
  return (
    <div className="max-w-4xl">
      <p className="text-xs font-medium uppercase tracking-widest text-signal mb-3">
        Multi-agent research
      </p>
      <h1 className="font-display text-4xl font-semibold text-ink leading-tight tracking-tight mb-4">
        Eight specialists.
        <br />
        One evidence trail.
      </h1>
      <p className="text-ink-muted text-base max-w-xl leading-relaxed mb-8">
        Fincast runs news, fundamentals, valuation, risk, technicals, portfolio, and macro agents
        against every query, then surfaces where they agree — and where they don&apos;t.
      </p>

      <div className="mb-10">
        <ConsensusStrip results={sampleConsensus} />
        <p className="mt-2 text-xs text-ink-faint">Example output for a single query, not live data</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {pages.map((page) => {
          const Icon = page.icon;
          return (
            <Link
              key={page.href}
              href={page.href}
              className="group flex items-start gap-3 p-4 rounded border border-line bg-paper-raised hover:border-line-strong transition-colors"
            >
              <Icon className="w-4.5 h-4.5 text-ink-faint mt-0.5 shrink-0" strokeWidth={1.75} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5">
                  <h2 className="font-medium text-sm text-ink">{page.title}</h2>
                  <ArrowUpRight className="w-3.5 h-3.5 text-ink-faint opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <p className="text-sm text-ink-muted mt-0.5">{page.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

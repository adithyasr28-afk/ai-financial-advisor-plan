"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Search, AlertTriangle, ChevronDown } from "lucide-react";
import { API_BASE_URL } from "../lib/api";
import { Card, CardHeader } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { StanceBadge } from "../components/ui/Badge";
import { ConsensusStrip } from "../components/ui/ConsensusStrip";
import { Skeleton, SkeletonLine } from "../components/ui/Skeleton";

interface OrchestrateResult {
  agent: string;
  query: string;
  summary: string;
  evidence: Array<Record<string, unknown>>;
  stance: string | null;
  confidence: number;
  sources: string[];
  assumptions: string[];
  limitations: string[];
  generated_at: string;
}

interface OrchestrateResponse {
  query: string;
  agents: string[];
  results: OrchestrateResult[];
  disagreements: Array<{ stances: string[]; message: string }>;
}

function CompanyAnalysisInner() {
  const searchParams = useSearchParams();
  const [symbol, setSymbol] = useState("AAPL");
  const [result, setResult] = useState<OrchestrateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(sym: string) {
    if (!sym.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/orchestrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: `${sym} comprehensive report` }),
      });
      if (!res.ok) throw new Error("Analysis failed");
      setResult(await res.json());
    } catch {
      setError("Analysis failed. Confirm the backend is reachable and try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const sp = searchParams.get("symbol");
    if (sp) {
      setSymbol(sp);
      handleAnalyze(sp);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Company Analysis</h1>
          <p className="text-sm text-ink-muted mt-1">Every agent weighs in, then the report writer flags where they disagree.</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-ink-faint absolute left-3 top-1/2 -translate-y-1/2" />
            <Input
              mono
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === "Enter" && handleAnalyze(symbol)}
              placeholder="AAPL"
              className="w-40 pl-8"
            />
          </div>
          <Button onClick={() => handleAnalyze(symbol)} disabled={loading}>
            {loading ? "Analyzing…" : "Analyze"}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-loss/30 bg-loss-soft text-loss text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
        </Card>
      )}

      {loading && !result && (
        <div className="space-y-3">
          <Card>
            <SkeletonLine width="40%" />
          </Card>
          {[0, 1, 2].map((i) => (
            <Card key={i}>
              <SkeletonLine width="25%" />
              <div className="mt-3">
                <Skeleton className="h-4 w-full" />
              </div>
            </Card>
          ))}
        </div>
      )}

      {result && (
        <div className="space-y-5">
          <Card>
            <CardHeader eyebrow={result.query} title={`${result.agents.length} agents consulted`} />
            <ConsensusStrip
              results={result.results.map((r) => ({ agent: r.agent, stance: r.stance, confidence: r.confidence }))}
            />
            {result.disagreements.length > 0 && (
              <div className="mt-4 p-3 rounded bg-warn-soft border border-warn/20 text-sm">
                <p className="font-medium text-warn mb-1">Disagreement detected</p>
                <p className="text-ink-muted">{result.disagreements[0].message}</p>
                <p className="text-xs text-ink-faint mt-1">Stances: {result.disagreements[0].stances.join(", ")}</p>
              </div>
            )}
          </Card>

          <div className="space-y-3">
            {result.results.map((agentResult, idx) => (
              <Card key={idx}>
                <div className="flex items-center justify-between gap-3 mb-2.5">
                  <h3 className="font-medium text-ink capitalize">{agentResult.agent.replace(/_/g, " ")}</h3>
                  <div className="flex items-center gap-2 shrink-0">
                    {agentResult.stance && <StanceBadge stance={agentResult.stance} />}
                    <span className="text-xs font-mono text-ink-faint tabular-nums">
                      {(agentResult.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-ink-muted leading-relaxed">{agentResult.summary}</p>

                {agentResult.evidence.length > 0 && (
                  <details className="group mt-3">
                    <summary className="cursor-pointer list-none flex items-center gap-1 text-xs font-medium text-signal hover:text-signal-hover">
                      <ChevronDown className="w-3.5 h-3.5 transition-transform group-open:rotate-180" />
                      Evidence ({agentResult.evidence.length})
                    </summary>
                    <div className="mt-2.5 space-y-2">
                      {agentResult.evidence.slice(0, 3).map((ev, i) => (
                        <pre
                          key={i}
                          className="p-2.5 bg-paper rounded border border-line text-xs text-ink-muted font-mono overflow-auto max-h-32 whitespace-pre-wrap"
                        >
                          {JSON.stringify(ev, null, 2)}
                        </pre>
                      ))}
                      {agentResult.evidence.length > 3 && (
                        <p className="text-xs text-ink-faint">+{agentResult.evidence.length - 3} more items</p>
                      )}
                    </div>
                  </details>
                )}

                {(agentResult.assumptions.length > 0 || agentResult.limitations.length > 0) && (
                  <details className="group mt-2">
                    <summary className="cursor-pointer list-none flex items-center gap-1 text-xs font-medium text-ink-faint hover:text-ink-muted">
                      <ChevronDown className="w-3.5 h-3.5 transition-transform group-open:rotate-180" />
                      Assumptions &amp; limitations
                    </summary>
                    <div className="mt-2.5 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {agentResult.assumptions.length > 0 && (
                        <div>
                          <p className="font-medium text-ink-muted mb-1 text-xs uppercase tracking-wide">Assumptions</p>
                          <ul className="space-y-1 text-ink-muted list-disc list-inside">
                            {agentResult.assumptions.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {agentResult.limitations.length > 0 && (
                        <div>
                          <p className="font-medium text-ink-muted mb-1 text-xs uppercase tracking-wide">Limitations</p>
                          <ul className="space-y-1 text-ink-muted list-disc list-inside">
                            {agentResult.limitations.map((l, i) => (
                              <li key={i}>{l}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </details>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function CompanyAnalysis() {
  return (
    <Suspense fallback={null}>
      <CompanyAnalysisInner />
    </Suspense>
  );
}

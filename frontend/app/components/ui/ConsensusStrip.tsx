import { stanceCategory } from "./Badge";

interface AgentResult {
  agent: string;
  stance: string | null;
  confidence: number;
}

const CATEGORY_BG: Record<string, string> = {
  gain: "#1E7B45",
  loss: "#B23A2E",
  neutral: "#8A94A0",
  warn: "#9A6B12",
};

const CATEGORY_LABEL: Record<string, string> = {
  gain: "constructive",
  loss: "cautionary",
  neutral: "neutral",
  warn: "conflicted",
};

/**
 * The signature element of this product: eight specialist agents each cast a
 * stance with a confidence level, and disagreement between them is a
 * first-class signal, not noise to average away. Segment width encodes
 * confidence (a louder vote takes more visual room), and color encodes
 * stance category - so the shape of the bar itself tells you whether the
 * agents broadly agree before you read a single word of summary.
 */
export function ConsensusStrip({ results }: { results: AgentResult[] }) {
  if (results.length === 0) return null;

  const counts: Record<string, number> = {};
  for (const r of results) {
    const cat = stanceCategory(r.stance);
    counts[cat] = (counts[cat] ?? 0) + 1;
  }
  const summary = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([cat, n]) => `${n} ${CATEGORY_LABEL[cat]}`)
    .join(" · ");

  return (
    <div>
      <div className="flex h-2 rounded-sm overflow-hidden gap-px bg-paper">
        {results.map((r, i) => {
          const cat = stanceCategory(r.stance);
          const weight = Math.max(r.confidence, 0.12);
          return (
            <div
              key={i}
              title={`${r.agent.replace(/_/g, " ")} — ${r.stance ?? "no stance"} (${Math.round(
                r.confidence * 100
              )}%)`}
              style={{ flexGrow: weight, backgroundColor: CATEGORY_BG[cat] }}
              className="min-w-[3px] h-full"
            />
          );
        })}
      </div>
      <p className="mt-1.5 text-xs text-ink-muted">
        {results.length} agents · {summary}
      </p>
    </div>
  );
}

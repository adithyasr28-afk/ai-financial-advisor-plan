type StanceCategory = "gain" | "loss" | "neutral" | "warn";

const STANCE_MAP: Record<string, StanceCategory> = {
  bullish: "gain",
  uptrend: "gain",
  bearish: "loss",
  downtrend: "loss",
  hold: "neutral",
  neutral: "neutral",
  conflict: "warn",
};

const CATEGORY_CLASSES: Record<StanceCategory, string> = {
  gain: "bg-gain-soft text-gain",
  loss: "bg-loss-soft text-loss",
  neutral: "bg-line/50 text-ink-muted",
  warn: "bg-warn-soft text-warn",
};

export function StanceBadge({ stance }: { stance: string }) {
  const category = STANCE_MAP[stance.toLowerCase()] ?? "neutral";
  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium capitalize ${CATEGORY_CLASSES[category]}`}
    >
      {stance}
    </span>
  );
}

export function StatusBadge({ active, onLabel = "Active", offLabel = "Paused" }: { active: boolean; onLabel?: string; offLabel?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium ${
        active ? "text-gain" : "text-ink-faint"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${active ? "bg-gain" : "bg-ink-faint"}`} />
      {active ? onLabel : offLabel}
    </span>
  );
}

export function stanceCategory(stance: string | null | undefined): StanceCategory {
  if (!stance) return "neutral";
  return STANCE_MAP[stance.toLowerCase()] ?? "neutral";
}

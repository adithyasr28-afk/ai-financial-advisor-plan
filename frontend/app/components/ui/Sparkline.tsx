interface SparklineProps {
  values: number[];
  width?: number;
  height?: number;
  className?: string;
}

/**
 * Minimal inline trend line. Deliberately axis-less and label-less - this is
 * a glance-level "which way is it moving" signal, not a full chart. Color
 * follows the domain convention (up = gain, down = loss) rather than a
 * decorative accent, so it reads correctly at a glance in a dense table.
 */
export function Sparkline({ values, width = 96, height = 32, className = "" }: SparklineProps) {
  if (!values || values.length < 2) {
    return (
      <div
        className={`flex items-center text-ink-faint text-xs ${className}`}
        style={{ width, height }}
      >
        —
      </div>
    );
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1);
  const points = values
    .map((v, i) => {
      const x = i * stepX;
      const y = height - ((v - min) / range) * (height - 4) - 2;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const rising = values[values.length - 1] >= values[0];
  const stroke = rising ? "#1E7B45" : "#B23A2E";

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      role="img"
      aria-label={rising ? "Trending up" : "Trending down"}
    >
      <polyline
        points={points}
        fill="none"
        stroke={stroke}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface EquityCurveChartProps {
  equity: number[];
  dates: string[];
  height?: number;
}

export function EquityCurveChart({ equity, dates, height = 220 }: EquityCurveChartProps) {
  if (equity.length < 2) return null;

  const width = 800;
  const padding = { top: 12, right: 12, bottom: 24, left: 48 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const min = Math.min(...equity);
  const max = Math.max(...equity);
  const range = max - min || 1;

  const stepX = innerWidth / (equity.length - 1);
  const points = equity
    .map((v, i) => {
      const x = padding.left + i * stepX;
      const y = padding.top + innerHeight - ((v - min) / range) * innerHeight;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const rising = equity[equity.length - 1] >= equity[0];
  const stroke = rising ? "#1E7B45" : "#B23A2E";

  const baselineY = padding.top + innerHeight - ((100 - min) / range) * innerHeight;
  const gridLines = [min, (min + max) / 2, max];

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
      {gridLines.map((v, i) => {
        const y = padding.top + innerHeight - ((v - min) / range) * innerHeight;
        return (
          <g key={i}>
            <line x1={padding.left} x2={width - padding.right} y1={y} y2={y} stroke="#DFE3E8" strokeWidth={1} />
            <text x={padding.left - 8} y={y + 3} fontSize="10" textAnchor="end" fill="#8A94A0" fontFamily="var(--font-mono)">
              {v.toFixed(0)}
            </text>
          </g>
        );
      })}

      {/* Starting-capital baseline, so a flat/declining strategy is visually obvious against it */}
      <line
        x1={padding.left}
        x2={width - padding.right}
        y1={baselineY}
        y2={baselineY}
        stroke="#C4CAD2"
        strokeWidth={1}
        strokeDasharray="3 3"
      />

      <polyline points={points} fill="none" stroke={stroke} strokeWidth={1.75} strokeLinejoin="round" />

      {dates.length > 1 && (
        <>
          <text x={padding.left} y={height - 4} fontSize="10" fill="#8A94A0" fontFamily="var(--font-mono)">
            {dates[0]}
          </text>
          <text x={width - padding.right} y={height - 4} fontSize="10" textAnchor="end" fill="#8A94A0" fontFamily="var(--font-mono)">
            {dates[dates.length - 1]}
          </text>
        </>
      )}
    </svg>
  );
}

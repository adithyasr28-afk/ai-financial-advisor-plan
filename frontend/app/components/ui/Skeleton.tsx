export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton animate-shimmer rounded ${className}`} />;
}

export function SkeletonLine({ width = "100%" }: { width?: string }) {
  return <div className="skeleton animate-shimmer rounded h-3" style={{ width }} />;
}

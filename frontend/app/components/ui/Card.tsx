import { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padded?: boolean;
}

export function Card({ children, className = "", padded = true, ...rest }: CardProps) {
  return (
    <div
      className={`bg-paper-raised border border-line rounded ${padded ? "p-5" : ""} ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  eyebrow,
  action,
}: {
  title: ReactNode;
  eyebrow?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-4 mb-4">
      <div>
        {eyebrow && (
          <p className="text-xs font-medium uppercase tracking-wide text-ink-faint mb-1">
            {eyebrow}
          </p>
        )}
        <h2 className="font-display text-base font-semibold text-ink">{title}</h2>
      </div>
      {action}
    </div>
  );
}

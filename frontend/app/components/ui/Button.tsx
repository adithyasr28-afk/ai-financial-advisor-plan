import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const base =
  "inline-flex items-center justify-center gap-2 rounded text-sm font-medium px-3.5 py-2 transition-colors disabled:opacity-40 disabled:pointer-events-none";

const variants: Record<Variant, string> = {
  primary: "bg-signal text-white hover:bg-signal-hover",
  secondary: "bg-paper-raised border border-line text-ink hover:border-line-strong",
  ghost: "text-ink-muted hover:text-ink hover:bg-line/40",
  danger: "text-loss hover:bg-loss-soft",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", className = "", ...rest }, ref) => (
    <button ref={ref} className={`${base} ${variants[variant]} ${className}`} {...rest} />
  )
);
Button.displayName = "Button";

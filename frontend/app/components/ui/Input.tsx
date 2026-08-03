import { InputHTMLAttributes, SelectHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  mono?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ mono = false, className = "", ...rest }, ref) => (
    <input
      ref={ref}
      className={`px-3 py-2 rounded border border-line bg-paper-raised text-ink text-sm placeholder:text-ink-faint focus:border-signal outline-none transition-colors ${
        mono ? "font-mono" : ""
      } ${className}`}
      {...rest}
    />
  )
);
Input.displayName = "Input";

export const Select = forwardRef<
  HTMLSelectElement,
  SelectHTMLAttributes<HTMLSelectElement>
>(({ className = "", ...rest }, ref) => (
  <select
    ref={ref}
    className={`px-3 py-2 rounded border border-line bg-paper-raised text-ink text-sm focus:border-signal outline-none transition-colors ${className}`}
    {...rest}
  />
));
Select.displayName = "Select";

export function Label({ children }: { children: string }) {
  return (
    <label className="block text-xs font-medium uppercase tracking-wide text-ink-faint mb-1.5">
      {children}
    </label>
  );
}

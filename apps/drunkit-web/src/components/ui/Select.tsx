import { forwardRef, useId, type SelectHTMLAttributes } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, id, className = "", children, ...rest }, ref) => {
    const generatedId = useId();
    const selectId = id ?? generatedId;

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={selectId} className="text-xs text-parchment/50">
            {label}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={`rounded-lg border bg-ink-800 px-3 py-2 text-parchment outline-none transition-colors ${
            error ? "border-rust-500 focus:border-rust-400" : "border-ink-600 focus:border-brass-500"
          } ${className}`}
          aria-invalid={!!error}
          {...rest}
        >
          {children}
        </select>
        {error && <p className="text-xs text-rust-400">{error}</p>}
      </div>
    );
  }
);
Select.displayName = "Select";

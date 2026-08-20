import { forwardRef, useId, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, className = "", ...rest }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs text-parchment/50">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`rounded-lg border bg-ink-800 px-3 py-2 text-parchment outline-none transition-colors placeholder:text-parchment/30 ${
            error ? "border-rust-500 focus:border-rust-400" : "border-ink-600 focus:border-brass-500"
          } ${className}`}
          aria-invalid={!!error}
          {...rest}
        />
        {error && <p className="text-xs text-rust-400">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";

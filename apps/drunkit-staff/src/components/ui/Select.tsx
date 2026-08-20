import { forwardRef, useId, type SelectHTMLAttributes } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, id, className = "", children, ...rest }, ref) => {
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
          className={`rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 text-parchment outline-none focus:border-brass-500 ${className}`}
          {...rest}
        >
          {children}
        </select>
      </div>
    );
  }
);
Select.displayName = "Select";

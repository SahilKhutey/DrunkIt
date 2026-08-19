import { forwardRef, type ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variantClasses: Record<Variant, string> = {
  primary: "bg-brass-500 text-ink-950 hover:bg-brass-400 disabled:bg-ink-700 disabled:text-parchment/40",
  secondary:
    "border border-ink-600 bg-ink-800 text-parchment hover:bg-ink-700 disabled:opacity-40",
  ghost: "text-parchment/70 hover:text-parchment hover:bg-ink-800 disabled:opacity-40",
  danger: "bg-rust-600 text-parchment hover:bg-rust-500 disabled:opacity-40",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2.5 text-sm",
};

/**
 * The one button component every page should use. Centralizing this
 * means a future visual tweak (radius, hover behavior, focus ring)
 * happens once instead of hunting through a dozen inline className
 * strings — see the pages already migrated to it (Login, Eligibility,
 * ProductDetail) versus ones not yet touched.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", loading, disabled, className = "", children, ...rest }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...rest}
      >
        {loading && (
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

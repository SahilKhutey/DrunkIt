/**
 * @drunkit/ui
 * Shared design primitives and accessible UI component kit for DrunkIt v0.1.
 */

import React, { ReactNode } from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  children,
  style,
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles: React.CSSProperties = {
    fontFamily: "inherit",
    fontWeight: 700,
    borderRadius: 8,
    border: "none",
    cursor: disabled ? "not-allowed" : "pointer",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    transition: "all 0.2s ease",
    opacity: disabled ? 0.6 : 1,
    ...style,
  };

  const sizeStyles: Record<string, React.CSSProperties> = {
    sm: { padding: "6px 12px", fontSize: 12 },
    md: { padding: "10px 18px", fontSize: 14 },
    lg: { padding: "14px 24px", fontSize: 16 },
  };

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      backgroundColor: "var(--accent-gold, #e5a93c)",
      color: "#0b0c10",
      boxShadow: "0 2px 10px rgba(229, 169, 60, 0.25)",
    },
    secondary: {
      backgroundColor: "var(--bg-surface, #14161d)",
      color: "var(--text-primary, #f3f4f6)",
      border: "1px solid var(--border-color, #2b3042)",
    },
    outline: {
      backgroundColor: "transparent",
      color: "var(--accent-gold, #e5a93c)",
      border: "1px solid var(--accent-gold, #e5a93c)",
    },
    ghost: {
      backgroundColor: "transparent",
      color: "var(--text-secondary, #9ca3af)",
    },
    danger: {
      backgroundColor: "rgba(239, 68, 68, 0.15)",
      color: "var(--accent-ruby, #ef4444)",
      border: "1px solid var(--accent-ruby, #ef4444)",
    },
  };

  return (
    <button
      style={{ ...baseStyles, ...sizeStyles[size], ...variantStyles[variant] }}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

export interface BadgeProps {
  variant?: "gold" | "emerald" | "ruby" | "amber" | "surface";
  children: ReactNode;
}

export function Badge({ variant = "gold", children }: BadgeProps) {
  const styles: Record<string, React.CSSProperties> = {
    gold: { backgroundColor: "rgba(229, 169, 60, 0.15)", color: "var(--accent-gold, #e5a93c)" },
    emerald: { backgroundColor: "rgba(16, 185, 129, 0.15)", color: "var(--accent-emerald, #10b981)" },
    ruby: { backgroundColor: "rgba(239, 68, 68, 0.15)", color: "var(--accent-ruby, #ef4444)" },
    amber: { backgroundColor: "rgba(217, 119, 6, 0.15)", color: "var(--accent-amber, #d97706)" },
    surface: { backgroundColor: "var(--bg-surface, #14161d)", color: "var(--text-secondary, #9ca3af)" },
  };

  return (
    <span
      style={{
        display: "inline-block",
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: "0.05em",
        textTransform: "uppercase",
        padding: "3px 8px",
        borderRadius: 6,
        ...styles[variant],
      }}
    >
      {children}
    </span>
  );
}

export interface CardProps {
  children: ReactNode;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export function Card({ children, style, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: "var(--bg-card, #1c1f2b)",
        border: "1px solid var(--border-color, #2b3042)",
        borderRadius: 14,
        padding: 20,
        cursor: onClick ? "pointer" : "default",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

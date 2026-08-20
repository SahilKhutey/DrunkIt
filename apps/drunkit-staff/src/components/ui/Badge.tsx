import type { ReactNode } from "react";

type Tone = "neutral" | "brass" | "sage" | "rust" | "copper";

const toneClasses: Record<Tone, string> = {
  neutral: "bg-ink-700 text-parchment/70",
  brass: "bg-brass-500/10 text-brass-400 border border-brass-600/30",
  sage: "bg-sage-500/10 text-sage-400 border border-sage-600/30",
  rust: "bg-rust-500/10 text-rust-400 border border-rust-600/30",
  copper: "bg-copper-500/10 text-copper-400 border border-copper-600/30",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}

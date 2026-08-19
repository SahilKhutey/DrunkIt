import type { ReactNode } from "react";

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-ink-700 py-16 text-center">
      <p className="font-display text-lg text-parchment">{title}</p>
      <p className="max-w-sm text-sm text-parchment/50">{body}</p>
      {action}
    </div>
  );
}

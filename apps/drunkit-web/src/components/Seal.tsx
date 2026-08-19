interface SealProps {
  label: string;
  tone?: "brass" | "sage" | "rust";
  size?: "sm" | "md";
}

const TONE_COLOR: Record<NonNullable<SealProps["tone"]>, string> = {
  brass: "text-brass-500",
  sage: "text-sage-500",
  rust: "text-rust-500",
};

const TONE_LABEL_COLOR: Record<NonNullable<SealProps["tone"]>, string> = {
  brass: "text-brass-400",
  sage: "text-sage-400",
  rust: "text-rust-400",
};

/**
 * The signature element for this design: a hexagonal seal, styled
 * after an excise duty stamp pressed into a bottle label. Used
 * anywhere the platform is vouching for something — verified seller,
 * verified listing, age-verified account — so trust states share one
 * consistent visual language instead of ad hoc checkmarks/pills. The
 * "rust" tone extends this to a matching visual language for failure
 * states (error boundary, blocked routes) rather than introducing an
 * unrelated icon style just for those.
 */
export function Seal({ label, tone = "brass", size = "sm" }: SealProps) {
  const dims = size === "sm" ? 20 : 28;

  return (
    <span className="inline-flex items-center gap-1.5" title={label}>
      <svg
        width={dims}
        height={dims}
        viewBox="0 0 24 24"
        className={`shrink-0 ${TONE_COLOR[tone]}`}
        aria-hidden="true"
      >
        <polygon
          points="12,1.5 21.1,6.75 21.1,17.25 12,22.5 2.9,17.25 2.9,6.75"
          fill="currentColor"
          fillOpacity="0.12"
          stroke="currentColor"
          strokeWidth="1.1"
        />
        <path
          d="M8 12.3l2.6 2.6L16.3 9"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span className={`text-xs font-medium ${TONE_LABEL_COLOR[tone]}`}>{label}</span>
    </span>
  );
}

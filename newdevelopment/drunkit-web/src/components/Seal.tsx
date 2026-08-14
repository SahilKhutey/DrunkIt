interface SealProps {
  label: string;
  tone?: "brass" | "sage";
  size?: "sm" | "md";
}

/**
 * The signature element for this design: a hexagonal seal, styled
 * after an excise duty stamp pressed into a bottle label. Used
 * anywhere the platform is vouching for something — verified seller,
 * verified listing, age-verified account — so trust states share one
 * consistent visual language instead of ad hoc checkmarks/pills.
 */
export function Seal({ label, tone = "brass", size = "sm" }: SealProps) {
  const dims = size === "sm" ? 20 : 28;
  const colorClass = tone === "brass" ? "text-brass-500" : "text-sage-500";
  const strokeClass = tone === "brass" ? "stroke-brass-500" : "stroke-sage-500";

  return (
    <span className="inline-flex items-center gap-1.5" title={label}>
      <svg
        width={dims}
        height={dims}
        viewBox="0 0 24 24"
        className={`shrink-0 ${colorClass}`}
        aria-hidden="true"
      >
        <polygon
          points="12,1.5 21.1,6.75 21.1,17.25 12,22.5 2.9,17.25 2.9,6.75"
          fill="currentColor"
          fillOpacity="0.12"
          className={strokeClass}
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
      <span className={`text-xs font-medium ${tone === "brass" ? "text-brass-400" : "text-sage-400"}`}>
        {label}
      </span>
    </span>
  );
}

export function SkeletonBlock({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-ink-800 ${className}`} />;
}

export function SkeletonCardGrid({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="overflow-hidden rounded-xl border border-ink-700">
          <SkeletonBlock className="aspect-square rounded-none" />
          <div className="space-y-2 p-3">
            <SkeletonBlock className="h-3 w-2/3" />
            <SkeletonBlock className="h-4 w-full" />
            <SkeletonBlock className="h-8 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

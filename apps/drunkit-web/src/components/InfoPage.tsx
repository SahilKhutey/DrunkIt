import { Link } from "react-router-dom";
import type { ReactNode } from "react";

interface Section {
  heading: string;
  body: ReactNode;
}

interface InfoPageProps {
  eyebrow: string;
  title: string;
  intro: string;
  sections: Section[];
}

/**
 * Shared template for informational/legal-adjacent pages (About,
 * Responsible Drinking). One layout, parameterized by content — the
 * kind of reuse a "page template" should mean, rather than each info
 * page rebuilding its own header/section structure.
 *
 * Content here is descriptive marketing/informational copy, not legal
 * terms — actual Terms of Service / Privacy Policy text should come
 * from counsel, not be drafted here.
 */
export function InfoPage({ eyebrow, title, intro, sections }: InfoPageProps) {
  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <p className="label-eyebrow">{eyebrow}</p>
      <h1 className="mt-2 font-display text-3xl text-parchment">{title}</h1>
      <p className="mt-3 text-sm leading-relaxed text-parchment/60">{intro}</p>

      <div className="mt-8 flex flex-col gap-8">
        {sections.map((s) => (
          <section key={s.heading}>
            <h2 className="font-display text-lg text-brass-400">{s.heading}</h2>
            <div className="mt-2 text-sm leading-relaxed text-parchment/70">{s.body}</div>
          </section>
        ))}
      </div>

      <Link to="/" className="mt-10 inline-block text-sm text-brass-400 hover:text-brass-300">
        ← Back to browsing
      </Link>
    </div>
  );
}

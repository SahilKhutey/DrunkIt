import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "DrunkIt — Alcohol Commerce & Intelligence Platform",
  description: "Discover premier single malts, craft gins, and fine spirits with real-time licensed retail availability and deterministic compliance.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

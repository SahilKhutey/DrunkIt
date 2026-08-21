import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "DrunkIt Brand House Intelligence — Taste Radars & Market Share",
  description: "Distillery brand portal for 6-axis taste radar benchmarking, SKU revenue tracking, and regional stockist penetration analytics.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

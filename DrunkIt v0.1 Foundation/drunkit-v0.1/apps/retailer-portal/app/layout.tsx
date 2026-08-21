import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "DrunkIt Retailer Portal — Store POS Sync & Order Fulfillment",
  description: "Licensed liquor retailer portal for POS inventory feeds, order queues, state machine fulfillment, and real-time store GMV analytics.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

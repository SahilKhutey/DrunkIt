import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "DrunkIt Driver App — Statutory Doorstep Verification & Delivery Handover",
  description: "Mobile driver handover app for point-of-delivery physical age verification, OTP authentication, and fail-closed statutory returns.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

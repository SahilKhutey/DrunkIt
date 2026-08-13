import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { TopBar } from "@/components/TopBar";

export const metadata: Metadata = {
  title: "FACCP Driver — Delivery Missions",
  description: "Real-time driver dispatch, GPS tracking & doorstep OTP verification",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-100 min-h-screen">
        <Providers>
          <div className="max-w-md mx-auto min-h-screen bg-white shadow-lg flex flex-col">
            <TopBar />
            <main className="flex-1 p-4 overflow-y-auto">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}

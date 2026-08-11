import './globals.css';
import React from 'react';

export const metadata = {
  title: 'FACCP State Regulatory Administration & Governance Platform',
  description: 'Federated Alcohol Commerce, Compliance & Trust Platform - Administrative Body',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}

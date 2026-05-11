import type { Metadata } from "next";
import { AppShell } from "@/components/shell/app-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "Synkra",
  description: "Video production management and review platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className="h-full antialiased"
      style={{
        "--font-inter": "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
        "--font-outfit": "Outfit, ui-sans-serif, system-ui, -apple-system, sans-serif",
      } as React.CSSProperties}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground font-sans">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

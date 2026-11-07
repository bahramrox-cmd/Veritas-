import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "GPT Web Chat",
  description: "Browser chat powered by Chat SDK and AI Gateway",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

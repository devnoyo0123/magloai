import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MagloAI - 음성 인식 및 요약 서비스",
  description: "YouTube 영상 자막 추출, 음성 파일 변환, AI 요약, 채팅 Q&A",
};

const NAV_ITEMS = [
  { href: "/upload", label: "📤 음성 업로드" },
  { href: "/youtube", label: "🎬 YouTube" },
  { href: "/history", label: "📋 저장된 요약" },
  { href: "/chat", label: "💬 채팅" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <body className="min-h-screen bg-background text-foreground">
        <header className="border-b">
          <div className="container mx-auto flex items-center gap-6 px-4 py-3">
            <Link href="/" className="text-xl font-bold">🎙️ MagloAI</Link>
            <nav className="flex gap-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}

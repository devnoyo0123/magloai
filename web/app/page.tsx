import Link from "next/link";

const FEATURES = [
  {
    href: "/upload",
    icon: "📤",
    title: "음성 파일 업로드",
    description: "음성 파일(mp3, wav, m4a)을 텍스트로 변환 후 AI 요약",
  },
  {
    href: "/youtube",
    icon: "🎬",
    title: "YouTube 요약",
    description: "YouTube URL 입력으로 자막 추출 후 한국어 요약",
  },
  {
    href: "/history",
    icon: "📋",
    title: "저장된 요약",
    description: "처리 완료된 요약본 목록 조회 및 관리",
  },
  {
    href: "/chat",
    icon: "💬",
    title: "채팅 Q&A",
    description: "스크립트를 기반으로 질문-답변",
  },
];

export default function HomePage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">🎙️ 음성 인식 및 요약 서비스</h1>
      <p className="text-muted-foreground mb-8">
        YouTube 영상 자막 추출, 음성 파일 변환, AI 요약, 채팅 Q&A
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {FEATURES.map((f) => (
          <Link
            key={f.href}
            href={f.href}
            className="block rounded-lg border p-6 hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <div className="text-3xl mb-2">{f.icon}</div>
            <h2 className="text-lg font-semibold mb-1">{f.title}</h2>
            <p className="text-sm text-muted-foreground">{f.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

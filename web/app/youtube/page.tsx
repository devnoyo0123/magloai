"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { processYouTube } from "@/lib/api-client";

export default function YouTubePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Awaited<ReturnType<typeof processYouTube>> | null>(null);

  const handleSubmit = async () => {
    if (!url) return;
    setLoading(true);
    setError(null);
    try {
      const data = await processYouTube(url);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "처리 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🎬 YouTube 요약</h1>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <Input
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Button onClick={handleSubmit} disabled={!url || loading} className="w-full">
            {loading ? "처리 중..." : "🚀 처리 시작"}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="mt-4 border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          <Card>
            <CardHeader><CardTitle>📝 요약</CardTitle></CardHeader>
            <CardContent><p className="whitespace-pre-wrap">{result.summary_text}</p></CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>📜 전체 스크립트</CardTitle></CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm max-h-96 overflow-y-auto">{result.transcript}</p>
            </CardContent>
          </Card>

          <p className="text-sm text-muted-foreground">저장 완료: {result.source_id}</p>
        </div>
      )}
    </div>
  );
}

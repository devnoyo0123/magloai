"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { processAudio } from "@/lib/api-client";
import AudioPlayer from "@/components/audio-player";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [sourceId, setSourceId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Awaited<ReturnType<typeof processAudio>> | null>(null);

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await processAudio(file, sourceId || undefined);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "처리 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">📤 음성 파일 업로드</h1>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div>
            <input
              type="file"
              accept=".mp3,.wav,.m4a,.ogg"
              onChange={(e) => {
                const f = e.target.files?.[0];
                setFile(f ?? null);
                if (f && !sourceId) setSourceId(f.name.replace(/\.[^.]+$/, ""));
              }}
              className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
            />
          </div>

          {file && (
            <audio controls className="w-full">
              <source src={URL.createObjectURL(file)} />
            </audio>
          )}

          <Input
            placeholder="소스 ID"
            value={sourceId}
            onChange={(e) => setSourceId(e.target.value)}
          />

          <Button onClick={handleSubmit} disabled={!file || loading} className="w-full">
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
              <p className="whitespace-pre-wrap text-sm max-h-80 overflow-y-auto">{result.transcript}</p>
            </CardContent>
          </Card>

          {result.segments && result.segments.length > 0 && (
            <Card>
              <CardHeader><CardTitle>🎵 인터랙티브 음성 플레이어</CardTitle></CardHeader>
              <CardContent>
                <AudioPlayer
                  audioSrc={`/api/audio/files/${result.source_id}_${result.audio_path?.split("_").pop()}`}
                  segments={result.segments}
                />
              </CardContent>
            </Card>
          )}

          <p className="text-sm text-muted-foreground">저장 완료: {result.source_id}</p>
        </div>
      )}
    </div>
  );
}

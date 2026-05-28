"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { fetchSummaries, fetchSummary, deleteSummary, type SummaryListItem, type SummaryDetail } from "@/lib/api-client";

export default function HistoryPage() {
  const [summaries, setSummaries] = useState<SummaryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, SummaryDetail>>({});

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchSummaries();
      setSummaries(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "불러오기 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const toggleExpand = async (sourceId: string) => {
    if (expandedId === sourceId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(sourceId);
    if (!details[sourceId]) {
      try {
        const detail = await fetchSummary(sourceId);
        setDetails((prev) => ({ ...prev, [sourceId]: detail }));
      } catch {
      }
    }
  };

  const handleDelete = async (sourceId: string) => {
    if (!confirm(`"${sourceId}" 삭제하시겠습니까?`)) return;
    try {
      await deleteSummary(sourceId);
      setSummaries((prev) => prev.filter((s) => s.source_id !== sourceId));
      if (expandedId === sourceId) setExpandedId(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "삭제 실패");
    }
  };

  if (loading) return <p className="text-muted-foreground">불러오는 중...</p>;
  if (error) return <p className="text-destructive">{error}</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">📋 저장된 요약</h1>
        <span className="text-sm text-muted-foreground">총 {summaries.length}개</span>
      </div>

      {summaries.length === 0 ? (
        <p className="text-muted-foreground">저장된 요약이 없습니다.</p>
      ) : (
        <div className="space-y-3">
          {summaries.map((s) => (
            <Card key={`${s.source_id}-${s.timestamp}`}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle
                    className="text-base cursor-pointer underline underline-offset-2 decoration-muted-foreground/40 hover:decoration-foreground transition-colors"
                    onClick={() => toggleExpand(s.source_id)}
                  >
                    {s.source_id}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{s.source_type}</Badge>
                    {s.timestamp && (
                      <span className="text-xs text-muted-foreground">
                        {new Date(s.timestamp).toLocaleString("ko-KR")}
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => handleDelete(s.source_id)}
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              </CardHeader>
              {expandedId === s.source_id && (
                <CardContent>
                  <Separator className="mb-3" />
                  {details[s.source_id] ? (
                    <div className="space-y-4">
                      {details[s.source_id].source_url && (
                        <p className="text-xs text-muted-foreground">
                          🔗 <a href={details[s.source_id].source_url} target="_blank" rel="noopener noreferrer" className="underline">{details[s.source_id].source_url}</a>
                        </p>
                      )}
                      {details[s.source_id].summary_text && (
                        <div>
                          <h3 className="font-semibold text-sm mb-1">📝 요약</h3>
                          <p className="text-sm whitespace-pre-wrap">{details[s.source_id].summary_text}</p>
                        </div>
                      )}
                      {details[s.source_id].transcript && (
                        <div>
                          <h3 className="font-semibold text-sm mb-1">📜 전체 스크립트</h3>
                          <p className="text-sm whitespace-pre-wrap max-h-60 overflow-y-auto text-muted-foreground">{details[s.source_id].transcript}</p>
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground">
                        저장 위치: summaries/{s.source_id}.json
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">불러오는 중...</p>
                  )}
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

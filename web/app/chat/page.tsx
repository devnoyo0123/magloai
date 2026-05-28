"use client";

import { useEffect, useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { fetchSummaries, sendChat, type SummaryListItem } from "@/lib/api-client";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [summaries, setSummaries] = useState<SummaryListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSummaries().then((data) => {
      setSummaries(data);
      if (data.length > 0) setSelectedId(data[0].source_id);
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedId || loading) return;
    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const allMessages = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await sendChat(allMessages, selectedId);
      setMessages((prev) => [...prev, { role: "assistant", content: res.message }]);
    } catch (e) {
      const err = e instanceof Error ? e.message : "알 수 없는 오류";
      const hint = err.includes("abort") ? "응답 시간이 초과되었습니다. 다시 시도해주세요." : err;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `오류: ${hint}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">💬 채팅 Q&A</h1>

      {summaries.length === 0 ? (
        <p className="text-muted-foreground">먼저 영상/음성을 처리하여 요약을 생성해주세요.</p>
      ) : (
        <>
          <div className="flex gap-2 mb-4">
            <select
              value={selectedId}
              onChange={(e) => {
                setSelectedId(e.target.value);
                setMessages([]);
              }}
              className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
            >
              {summaries.map((s) => (
                <option key={`${s.source_id}-${s.timestamp}`} value={s.source_id}>
                  {s.source_id} - {s.timestamp ? new Date(s.timestamp).toLocaleDateString("ko-KR") : "N/A"}
                </option>
              ))}
            </select>
            <Button
              variant="outline"
              onClick={() => setMessages([])}
            >
              🔄 초기화
            </Button>
          </div>

          <Card className="mb-4">
            <CardContent className="pt-6">
              <div className="h-96 overflow-y-auto space-y-4">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg px-4 py-2 text-sm text-muted-foreground">
                      답변 생성 중...
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="영상 내용에 대해 질문하세요..."
              className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
              disabled={loading}
            />
            <Button onClick={handleSend} disabled={loading || !input.trim()}>
              전송
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

const API_BASE = "/api";

export interface SummaryListItem {
  source_id: string;
  source_type: string;
  summary_text: string | null;
  timestamp: string | null;
  has_audio: boolean;
  has_transcript: boolean;
}

export interface SummaryDetail {
  source_id: string;
  source_url: string;
  source_type: string;
  summary_text: string | null;
  transcript: string | null;
  segments: Array<{ start: number; end: number; text: string }> | null;
  audio_file_path: string | null;
  timestamp: string | null;
  model: string | null;
}

export async function fetchSummaries(): Promise<SummaryListItem[]> {
  const res = await fetch(`${API_BASE}/summaries`);
  if (!res.ok) throw new Error("Failed to fetch summaries");
  return res.json();
}

export async function fetchSummary(sourceId: string): Promise<SummaryDetail> {
  const res = await fetch(`${API_BASE}/summaries/${encodeURIComponent(sourceId)}`);
  if (!res.ok) throw new Error("Failed to fetch summary");
  return res.json();
}

export async function deleteSummary(sourceId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/summaries/${encodeURIComponent(sourceId)}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete summary");
}

export async function processYouTube(url: string): Promise<{
  source_id: string;
  summary_text: string;
  transcript: string;
}> {
  const res = await fetch(`${API_BASE}/youtube/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error("Failed to process YouTube");
  return res.json();
}

export async function processAudio(file: File, sourceId?: string): Promise<{
  source_id: string;
  summary_text: string;
  transcript: string;
  segments: Array<{ start: number; end: number; text: string }> | null;
  audio_path: string | null;
}> {
  const formData = new FormData();
  formData.append("file", file);
  if (sourceId) formData.append("source_id", sourceId);

  const res = await fetch(`${API_BASE}/audio/process`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to process audio");
  return res.json();
}

export async function sendChat(
  messages: Array<{ role: string; content: string }>,
  summaryId: string
): Promise<{ message: string }> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages, summary_id: summaryId }),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error("Failed to send chat");
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

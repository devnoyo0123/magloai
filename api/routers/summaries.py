from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import unicodedata

router = APIRouter()


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFC", s)


class SummaryResponse(BaseModel):
    source_id: str
    source_url: str
    source_type: str
    summary_text: Optional[str] = None
    transcript: Optional[str] = None
    segments: Optional[List[dict]] = None
    audio_file_path: Optional[str] = None
    timestamp: Optional[str] = None
    model: Optional[str] = None


class SummaryListItem(BaseModel):
    source_id: str
    source_type: str
    summary_text: Optional[str] = None
    timestamp: Optional[str] = None
    has_audio: bool = False
    has_transcript: bool = False


@router.get("/summaries", response_model=List[SummaryListItem])
async def list_summaries():
    from api.main import repository
    summaries = repository.load_all()
    return [
        SummaryListItem(
            source_id=_normalize(s.source_id or "unknown"),
            source_type=s.source_type or "unknown",
            summary_text=(s.summary_text[:200] + "...") if s.summary_text and len(s.summary_text) > 200 else s.summary_text,
            timestamp=s.timestamp.isoformat() if s.timestamp else None,
            has_audio=bool(s.audio_file_path),
            has_transcript=bool(s.transcript),
        )
        for s in summaries
    ]


@router.get("/summaries/{source_id}", response_model=SummaryResponse)
async def get_summary(source_id: str):
    from api.main import repository
    summaries = repository.load_all()
    for s in summaries:
        if _normalize(s.source_id) == _normalize(source_id):
            return SummaryResponse(
                source_id=_normalize(s.source_id),
                source_url=s.source_url,
                source_type=s.source_type,
                summary_text=s.summary_text,
                transcript=s.transcript,
                segments=[seg.to_dict() for seg in s.segments] if s.segments else None,
                audio_file_path=s.audio_file_path,
                timestamp=s.timestamp.isoformat() if s.timestamp else None,
                model=s.model,
            )
    raise HTTPException(status_code=404, detail="Summary not found")


@router.delete("/summaries/{source_id}")
async def delete_summary(source_id: str):
    from api.main import repository
    summaries = repository.load_all()
    for s in summaries:
        if _normalize(s.source_id) == _normalize(source_id):
            repository.delete(s)
            return {"success": True, "deleted": _normalize(source_id)}
    raise HTTPException(status_code=404, detail="Summary not found")

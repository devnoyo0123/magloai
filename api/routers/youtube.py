from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class YouTubeRequest(BaseModel):
    url: str


class YouTubeResponse(BaseModel):
    source_id: str
    source_url: str
    summary_text: str
    transcript: str
    json_path: str


@router.post("/youtube/process", response_model=YouTubeResponse)
async def process_youtube(req: YouTubeRequest):
    from api.main import process_youtube_use_case
    try:
        summary, json_path = process_youtube_use_case.execute(req.url)
        return YouTubeResponse(
            source_id=summary.source_id,
            source_url=summary.source_url,
            summary_text=summary.summary_text,
            transcript=summary.transcript or "",
            json_path=str(json_path),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

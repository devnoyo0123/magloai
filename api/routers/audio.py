import tempfile
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AudioProcessResponse(BaseModel):
    source_id: str
    source_url: str
    summary_text: str
    transcript: str
    segments: Optional[list] = None
    json_path: str
    audio_path: Optional[str] = None


@router.post("/audio/process", response_model=AudioProcessResponse)
async def process_audio(
    file: UploadFile = File(...),
    source_id: str = Form(None),
):
    from api.main import process_audio_use_case

    if not source_id:
        source_id = Path(file.filename).stem if file.filename else "unknown"

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix if file.filename else ".mp3") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        summary, json_path, audio_path = process_audio_use_case.execute(
            audio_file_path=tmp_path,
            source_id=source_id,
            source_url="",
            source_type="audio"
        )
        return AudioProcessResponse(
            source_id=summary.source_id,
            source_url=summary.source_url,
            summary_text=summary.summary_text,
            transcript=summary.transcript or "",
            segments=[seg.to_dict() for seg in summary.segments] if summary.segments else None,
            json_path=str(json_path),
            audio_path=str(audio_path) if audio_path else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/audio/files/{filename}")
async def get_audio_file(filename: str):
    audio_dir = Path("summaries/audio_files")
    file_path = audio_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        filename=filename,
    )

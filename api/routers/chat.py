from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import unicodedata
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFC", s)


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    summary_id: str


class ChatResponse(BaseModel):
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    from api.main import chat_use_case, repository
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Chat request received: summary_id={req.summary_id}, messages_count={len(req.messages)}")

    try:
        summaries = repository.load_all()
        logger.info(f"Loaded {len(summaries)} summaries")

        summary = None
        for s in summaries:
            if _normalize(s.source_id) == _normalize(req.summary_id):
                summary = s
                break

        if not summary:
            logger.warning(f"Summary not found: {req.summary_id}")
            raise HTTPException(status_code=404, detail="Summary not found")

        logger.info(f"Summary found: {summary.source_id}")

        response = chat_use_case.chat(messages=req.messages, summary=summary)
        logger.info(f"Chat response generated successfully")

        return ChatResponse(message=response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/clear")
async def clear_chat():
    from api.main import chat_use_case
    chat_use_case.clear_history()
    return {"success": True}

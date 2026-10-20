
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.rag_service import answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/")
def chat(request: ChatRequest):
    try:
        return answer_question(request.question.strip())

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Question answering failed")

        # TEMPORARY: expose the actual error for local debugging.
        raise HTTPException(
            status_code=502,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

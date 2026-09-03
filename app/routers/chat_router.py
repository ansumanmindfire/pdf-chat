"""API router for conversational RAG chat endpoint."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import logger
from app.database.session import get_db
from app.repositories import ChatRepository
from app.services.rag_service import ask_pdf
from app.schemas.schemas import ChatRequest, ChatResponse
from app.exceptions.custom_exceptions import (
    SessionNotFoundException,
    RAGGenerationException,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask Question via RAG Chat",
    description="Processes user question, retrieves context from vector DB, includes past chat history, and returns AI answer with page citations.",
)
def chat_with_pdf(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Processes a user question against document vector store using chat session memory.

    Args:
        request (ChatRequest): Request payload containing question and session_id.
        db (Session): Database session dependency.

    Returns:
        ChatResponse: Object containing AI answer text, cited page numbers, and session_id.

    Raises:
        SessionNotFoundException: If session_id is not found in database.
        RAGGenerationException: If vector search or LLM answer generation fails.
    """
    # Verify chat session exists in database
    session_record = ChatRepository.get_session_by_id(db, request.session_id)
    if not session_record:
        raise SessionNotFoundException(f"Chat session '{request.session_id}' not found.")

    try:
        result = ask_pdf(
            question=request.question,
            session_id=request.session_id,
        )

        return ChatResponse(
            answer=result["answer"],
            source_pages=result["source_pages"],
            session_id=result["session_id"],
        )

    except Exception as e:
        logger.error(f"Error during RAG generation for session '{request.session_id}': {e}")
        raise RAGGenerationException(str(e))

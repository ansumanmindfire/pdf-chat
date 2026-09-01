"""API router for chat sessions, conversational RAG Q&A, and chat history endpoints."""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import logger
from app.database.session import get_db
from app.repositories import DocumentRepository, ChatRepository
from app.services.rag_service import ask_pdf
from app.schemas.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
)
from app.exceptions.custom_exceptions import (
    DocumentNotFoundException,
    SessionNotFoundException,
    RAGGenerationException,
)

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Chat Session",
    description="Creates a new chat session linked to a specific uploaded PDF document.",
)
def create_session(
    body: ChatSessionCreate,
    db: Session = Depends(get_db),
):
    """Creates a new chat session for a document."""
    doc = DocumentRepository.get_by_id(db, body.document_id)
    if not doc:
        raise DocumentNotFoundException(body.document_id)

    session_name = body.session_name or f"Chat on {doc.filename}"
    chat_session = ChatRepository.create_session(
        db=db,
        document_id=body.document_id,
        session_name=session_name,
    )
    return chat_session


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Ask Question (RAG)",
    description="Queries the PDF document using LCEL RAG chain, includes chat history memory, and returns answer + page citations.",
)
def query_rag(
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """Executes RAG Q&A with conversational memory support."""
    if body.session_id:
        session_rec = ChatRepository.get_session_by_id(db, body.session_id)
        if not session_rec:
            raise SessionNotFoundException(body.session_id)

    try:
        result = ask_pdf(
            question=body.question,
            session_id=body.session_id,
        )
        return ChatResponse(
            answer=result["answer"],
            source_pages=result["source_pages"],
            session_id=result.get("session_id"),
        )
    except (DocumentNotFoundException, SessionNotFoundException):
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise RAGGenerationException(str(e))


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    summary="Get Chat Session History",
    description="Retrieves the full list of past user questions and AI responses for a chat session.",
)
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Fetches chat message history for a session."""
    session_rec = ChatRepository.get_session_by_id(db, session_id)
    if not session_rec:
        raise SessionNotFoundException(session_id)

    messages = ChatRepository.get_session_messages(db, session_id)
    msg_responses = [ChatMessageResponse.model_validate(msg) for msg in messages]

    return ChatHistoryResponse(
        session_id=session_id,
        messages=msg_responses,
    )

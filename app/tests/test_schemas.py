"""Unit tests for Pydantic request and response schemas."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas.schemas import UploadResponse, ChatRequest, ChatResponse


def test_upload_response_valid():
    """Tests UploadResponse schema validation with valid data."""
    now = datetime.now(timezone.utc)
    res = UploadResponse(
        session_id="sess-123",
        document_id="doc-456",
        filename="test.pdf",
        created_at=now,
    )
    assert res.session_id == "sess-123"
    assert res.document_id == "doc-456"
    assert res.filename == "test.pdf"


def test_chat_request_valid():
    """Tests ChatRequest schema validation with valid fields."""
    req = ChatRequest(question="What is RAG?", session_id="sess-789")
    assert req.question == "What is RAG?"
    assert req.session_id == "sess-789"


def test_chat_request_invalid_empty():
    """Tests ChatRequest raises ValidationError when fields are empty."""
    with pytest.raises(ValidationError):
        ChatRequest(question="", session_id="sess-789")

    with pytest.raises(ValidationError):
        ChatRequest(question="Hello", session_id="")


def test_chat_response_valid():
    """Tests ChatResponse schema serialization."""
    res = ChatResponse(
        answer="RAG stands for Retrieval-Augmented Generation.",
        source_pages=[1],
        session_id="sess-789",
    )
    assert res.answer.startswith("RAG")
    assert res.source_pages == [1]
    assert res.session_id == "sess-789"

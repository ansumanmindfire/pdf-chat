"""Pydantic schemas for request and response validation in FastAPI endpoints."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class UploadResponse(BaseModel):
    """Response schema for PDF upload, vector indexing, and session initialization."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str = Field(..., description="Unique chat session ID (UUID)")
    document_id: str = Field(..., description="Unique document ID (UUID)")
    filename: str = Field(..., description="Original filename of the uploaded PDF")
    created_at: datetime = Field(..., description="Timestamp when upload and session were created")


class ChatRequest(BaseModel):
    """Request schema for sending a question to the RAG chat service."""

    question: str = Field(..., min_length=1, description="User question string")
    session_id: str = Field(..., min_length=1, description="Target chat session ID")


class ChatResponse(BaseModel):
    """Response schema returned by the RAG chat service."""

    answer: str = Field(..., description="AI-generated answer text")
    source_pages: List[int] = Field(default_factory=list, description="List of 1-indexed PDF page numbers cited")
    session_id: str = Field(..., description="Chat session ID associated with the turn")

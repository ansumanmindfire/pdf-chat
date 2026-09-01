"""Pydantic schemas for request and response validation in FastAPI endpoints."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentResponse(BaseModel):
    """Response schema for uploaded PDF document details."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique document ID (UUID)")
    filename: str = Field(..., description="Original filename of the uploaded PDF")
    file_path: str = Field(..., description="Saved file path on disk")
    faiss_index_path: str = Field(..., description="FAISS vector index directory path")
    created_at: datetime = Field(..., description="Timestamp when the document was uploaded")


class DocumentListResponse(BaseModel):
    """Response schema for a list of uploaded documents."""

    documents: List[DocumentResponse] = Field(default_factory=list, description="List of document records")


class ChatSessionCreate(BaseModel):
    """Request schema for creating a new chat session."""

    document_id: str = Field(..., description="Target document ID to link the chat session to")
    session_name: Optional[str] = Field(default="New Chat Session", description="Display name for the session")


class ChatSessionResponse(BaseModel):
    """Response schema for chat session details."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique chat session ID (UUID)")
    session_name: str = Field(..., description="Session display name")
    document_id: str = Field(..., description="Linked document ID")
    created_at: datetime = Field(..., description="Timestamp when session was created")


class ChatRequest(BaseModel):
    """Request schema for sending a user question to the RAG service."""

    question: str = Field(..., min_length=1, description="User question string")
    session_id: Optional[str] = Field(default=None, description="Chat session ID for conversational memory")
    document_id: Optional[str] = Field(default=None, description="Document ID to query against")


class ChatResponse(BaseModel):
    """Response schema returned by the RAG chat service."""

    answer: str = Field(..., description="AI-generated answer text")
    source_pages: List[int] = Field(default_factory=list, description="List of 1-indexed PDF page numbers cited")
    session_id: Optional[str] = Field(default=None, description="Chat session ID associated with the turn")


class ChatMessageResponse(BaseModel):
    """Response schema for an individual saved chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique message ID")
    session_id: str = Field(..., description="Associated chat session ID")
    sender: str = Field(..., description="Sender role ('user' or 'ai')")
    content: str = Field(..., description="Message text content")
    timestamp: datetime = Field(..., description="Timestamp when message was created")


class ChatHistoryResponse(BaseModel):
    """Response schema for retrieving full chat history of a session."""

    session_id: str = Field(..., description="Target chat session ID")
    messages: List[ChatMessageResponse] = Field(default_factory=list, description="List of conversation messages")

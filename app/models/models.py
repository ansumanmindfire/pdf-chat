"""SQLAlchemy ORM models for Documents, Chat Sessions, and Chat Messages."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Base declarative class for ORM models
Base = declarative_base()


def generate_uuid() -> str:
    """Generates a string UUID hex representation.

    Returns:
        str: Unique UUID string.
    """
    return uuid.uuid4().hex


class DocumentModel(Base):
    """Stores metadata for uploaded PDF files."""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    faiss_index_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sessions = relationship("ChatSessionModel", back_populates="document", cascade="all, delete-orphan")


class ChatSessionModel(Base):
    """Stores chat session records linked to a PDF document."""

    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_name = Column(String(255), nullable=False, default="New Chat Session")
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("DocumentModel", back_populates="sessions")
    messages = relationship(
        "ChatMessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessageModel.timestamp",
    )


class ChatMessageModel(Base):
    """Stores individual user questions and AI responses for a session."""

    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # 'user' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("ChatSessionModel", back_populates="messages")

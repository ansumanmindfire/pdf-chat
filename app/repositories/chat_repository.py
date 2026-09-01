"""Repository for ChatSessionModel and ChatMessageModel database operations."""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.config import logger
from app.models.models import ChatSessionModel, ChatMessageModel


class ChatRepository:
    """Encapsulates CRUD operations for Chat Sessions and Messages."""

    @staticmethod
    def create_session(
        db: Session,
        document_id: str,
        session_name: str = "New PDF Chat Session",
    ) -> ChatSessionModel:
        """Creates and persists a new chat session.

        Args:
            db (Session): Database session.
            document_id (str): Linked document ID.
            session_name (str): Session display name.

        Returns:
            ChatSessionModel: Persisted chat session record.
        """
        session = ChatSessionModel(
            document_id=document_id,
            session_name=session_name,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"ChatRepository: Created session '{session.id}' for document '{document_id}'.")
        return session

    @staticmethod
    def get_session_by_id(db: Session, session_id: str) -> Optional[ChatSessionModel]:
        """Fetches a chat session by ID.

        Args:
            db (Session): Database session.
            session_id (str): Chat session ID.

        Returns:
            Optional[ChatSessionModel]: Chat session record or None.
        """
        return db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()

    @staticmethod
    def save_message(
        db: Session,
        session_id: str,
        sender: str,
        content: str,
    ) -> ChatMessageModel:
        """Saves a user or ai message to the session.

        Args:
            db (Session): Database session.
            session_id (str): Chat session ID.
            sender (str): Message sender ('user' or 'ai').
            content (str): Message content text.

        Returns:
            ChatMessageModel: Persisted message record.
        """
        if sender not in ("user", "ai"):
            raise ValueError(f"Invalid sender '{sender}'. Must be 'user' or 'ai'.")

        msg = ChatMessageModel(
            session_id=session_id,
            sender=sender,
            content=content,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        logger.info(f"ChatRepository: Saved message '{msg.id}' ({sender}) in session '{session_id}'.")
        return msg

    @staticmethod
    def get_history_messages(
        db: Session,
        session_id: str,
        limit: int = 10,
    ) -> List[BaseMessage]:
        """Fetches past chat messages for a session formatted as LangChain HumanMessage/AIMessage objects.

        Args:
            db (Session): Database session.
            session_id (str): Chat session ID.
            limit (int): Maximum number of recent messages to retrieve.

        Returns:
            List[BaseMessage]: List of LangChain messages for chat memory.
        """
        messages_query = (
            db.query(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.timestamp.desc())
            .limit(limit)
            .all()
        )

        messages_query.reverse()

        langchain_messages: List[BaseMessage] = []
        for msg in messages_query:
            if msg.sender == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.sender == "ai":
                langchain_messages.append(AIMessage(content=msg.content))

        return langchain_messages

    @staticmethod
    def get_session_messages(
        db: Session,
        session_id: str,
    ) -> List[ChatMessageModel]:
        """Fetches all message ORM records for a session (for API history serialization).

        Args:
            db (Session): Database session.
            session_id (str): Chat session ID.

        Returns:
            List[ChatMessageModel]: List of message records ordered by timestamp.
        """
        return (
            db.query(ChatMessageModel)
            .filter(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.timestamp.asc())
            .all()
        )

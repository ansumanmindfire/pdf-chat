"""Unit tests for DocumentRepository and ChatRepository CRUD operations."""

import pytest
from sqlalchemy.orm import Session
from app.repositories import DocumentRepository, ChatRepository


def test_document_repository_crud(db_session: Session):
    """Tests creating and querying document records."""
    doc = DocumentRepository.create(
        db=db_session,
        filename="test_repo.pdf",
        file_path="data/uploads/test_repo.pdf",
        faiss_index_path="data/faiss_index/test_repo",
    )
    assert doc.id is not None
    assert doc.filename == "test_repo.pdf"

    fetched = DocumentRepository.get_by_id(db_session, doc.id)
    assert fetched is not None
    assert fetched.id == doc.id

    all_docs = DocumentRepository.get_all(db_session)
    assert len(all_docs) == 1
    assert all_docs[0].id == doc.id


def test_chat_repository_crud(db_session: Session):
    """Tests session creation, message saving, and history retrieval."""
    doc = DocumentRepository.create(
        db=db_session,
        filename="chat_doc.pdf",
        file_path="data/uploads/chat_doc.pdf",
        faiss_index_path="data/faiss_index/chat_doc",
    )

    session = ChatRepository.create_session(
        db=db_session,
        document_id=doc.id,
        session_name="Test Session",
    )
    assert session.id is not None
    assert session.document_id == doc.id

    fetched_sess = ChatRepository.get_session_by_id(db_session, session.id)
    assert fetched_sess is not None

    # Save User message
    user_msg = ChatRepository.save_message(
        db=db_session,
        session_id=session.id,
        sender="user",
        content="What is in this document?",
    )
    assert user_msg.sender == "user"

    # Save AI message
    ai_msg = ChatRepository.save_message(
        db=db_session,
        session_id=session.id,
        sender="ai",
        content="This document contains test data.",
    )
    assert ai_msg.sender == "ai"

    # Test invalid sender validation
    with pytest.raises(ValueError):
        ChatRepository.save_message(
            db=db_session,
            session_id=session.id,
            sender="invalid_role",
            content="Some Content",
        )

    # Verify history formatted for LangChain
    history = ChatRepository.get_history_messages(db_session, session.id)
    assert len(history) == 2
    assert history[0].content == "What is in this document?"
    assert history[1].content == "This document contains test data."

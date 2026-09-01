"""Repository for DocumentModel database operations."""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config import logger
from app.models.models import DocumentModel


class DocumentRepository:
    """Encapsulates CRUD operations for uploaded Document metadata records."""

    @staticmethod
    def create(
        db: Session,
        filename: str,
        file_path: str,
        faiss_index_path: str,
    ) -> DocumentModel:
        """Creates and persists a new document record.

        Args:
            db (Session): Database session.
            filename (str): Original PDF filename.
            file_path (str): File path on disk.
            faiss_index_path (str): FAISS index storage path.

        Returns:
            DocumentModel: Persisted document ORM instance.
        """
        doc = DocumentModel(
            filename=filename,
            file_path=file_path,
            faiss_index_path=faiss_index_path,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info(f"DocumentRepository: Created record '{doc.id}' for '{filename}'.")
        return doc

    @staticmethod
    def get_by_id(db: Session, document_id: str) -> Optional[DocumentModel]:
        """Fetches a document record by ID.

        Args:
            db (Session): Database session.
            document_id (str): Document ID string.

        Returns:
            Optional[DocumentModel]: Document record or None.
        """
        return db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    @staticmethod
    def get_all(db: Session) -> List[DocumentModel]:
        """Fetches all uploaded document records ordered by creation date.

        Args:
            db (Session): Database session.

        Returns:
            List[DocumentModel]: List of all document records.
        """
        return db.query(DocumentModel).order_by(DocumentModel.created_at.desc()).all()

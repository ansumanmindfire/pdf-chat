"""API router for document upload and session initialization."""

import os
import uuid
from fastapi import APIRouter, File, UploadFile, Depends, status
from sqlalchemy.orm import Session

from app.config import settings, logger
from app.constants import ALLOWED_EXTENSIONS
from app.database.session import get_db
from app.repositories import DocumentRepository, ChatRepository
from app.services.pdf_service import load_and_chunk_pdf
from app.services.vector_service import create_faiss_vector_store
from app.schemas.schemas import UploadResponse
from app.exceptions.custom_exceptions import InvalidFileException, PDFProcessingException

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF and Create Session",
    description="Uploads a PDF file, parses chunks, builds FAISS vector index, and auto-initializes a chat session.",
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Handles PDF file upload, vector indexing, and automatic chat session creation.

    Args:
        file (UploadFile): Uploaded PDF file stream.
        db (Session): Database session dependency.

    Returns:
        UploadResponse: Object containing session_id, document_id, filename, and created_at.

    Raises:
        InvalidFileException: If uploaded file is empty or not a PDF.
        PDFProcessingException: If PDF parsing or vector indexing fails.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileException(f"Only PDF files ({', '.join(ALLOWED_EXTENSIONS)}) are allowed.")

    # Generate unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        # Save file to disk
        contents = await file.read()
        if not contents:
            raise InvalidFileException("Uploaded PDF file is empty.")

        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Saved uploaded file to '{file_path}'. Parsing chunks...")

        # Parse & Chunk PDF
        chunks = load_and_chunk_pdf(file_path)

        # Build FAISS Vector Store
        index_path = f"data/faiss_index_{uuid.uuid4().hex[:8]}"
        create_faiss_vector_store(chunks, index_path=index_path)

        # Create Document Record in DB
        doc_record = DocumentRepository.create(
            db=db,
            filename=file.filename,
            file_path=file_path,
            faiss_index_path=index_path,
        )

        chat_session = ChatRepository.create_session(
            db=db,
            document_id=doc_record.id,
            session_name=f"Chat - {file.filename}",
        )

        return UploadResponse(
            session_id=chat_session.id,
            document_id=doc_record.id,
            filename=doc_record.filename,
            created_at=chat_session.created_at,
        )

    except InvalidFileException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded PDF: {e}")
        raise PDFProcessingException(str(e))

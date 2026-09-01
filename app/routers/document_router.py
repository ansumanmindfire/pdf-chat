"""API router for document upload and document management endpoints."""

import os
import uuid
from fastapi import APIRouter, File, UploadFile, Depends, status
from sqlalchemy.orm import Session

from app.config import settings, logger
from app.constants import ALLOWED_EXTENSIONS
from app.database.session import get_db
from app.repositories import DocumentRepository
from app.services.pdf_service import load_and_chunk_pdf
from app.services.vector_service import create_faiss_vector_store
from app.schemas.schemas import DocumentResponse, DocumentListResponse
from app.exceptions.custom_exceptions import InvalidFileException, PDFProcessingException

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Process PDF Document",
    description="Uploads a PDF file, parses page chunks, builds FAISS vector store, and saves document record.",
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Handles PDF file upload, chunk parsing, vector indexing, and database record creation."""
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

        # Create Document Record in DB via Repository
        doc_record = DocumentRepository.create(
            db=db,
            filename=file.filename,
            file_path=file_path,
            faiss_index_path=index_path,
        )

        return doc_record

    except InvalidFileException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded PDF: {e}")
        raise PDFProcessingException(str(e))


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List All Documents",
    description="Retrieves a list of all uploaded PDF document records.",
)
def list_documents(db: Session = Depends(get_db)):
    """Fetches all uploaded documents from the database."""
    documents = DocumentRepository.get_all(db)
    return DocumentListResponse(documents=documents)

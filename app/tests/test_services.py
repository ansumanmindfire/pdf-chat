"""Unit tests for pdf_service core functionality using mocks."""

from unittest.mock import patch, MagicMock
import pytest
from app.services.pdf_service import load_and_chunk_pdf


@patch("app.services.pdf_service.PdfReader")
def test_pdf_chunking_service(mock_pdf_reader):
    """Tests reading and chunking a PDF using PyPDF mocks."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "FastAPI and LangChain RAG Testing PDF Chunk."
    mock_pdf_reader.return_value.pages = [mock_page]

    chunks = load_and_chunk_pdf("dummy.pdf", chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 0
    assert "page" in chunks[0].metadata
    assert chunks[0].metadata["page"] == 1
    assert "FastAPI" in chunks[0].page_content


def test_pdf_chunking_file_not_found():
    """Tests FileNotFoundError when opening non-existent PDF file."""
    with pytest.raises(FileNotFoundError):
        load_and_chunk_pdf("non_existent_path.pdf")

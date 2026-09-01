"""PDF parsing and text chunking service."""

from typing import List
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings, logger


def load_and_chunk_pdf(
    pdf_path: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> List[Document]:
    """Reads a PDF file page by page, attaches page metadata, and splits text into chunks.

    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Character size per chunk.
        chunk_overlap (int): Overlap between adjacent chunks.

    Returns:
        List[Document]: List of LangChain Document chunks with page metadata.

    Raises:
        FileNotFoundError: If pdf_path does not exist.
        ValueError: If PDF contains no extractable text.
    """
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF file at '{pdf_path}': {e}")
        raise FileNotFoundError(f"Could not read PDF file at '{pdf_path}': {e}") from e

    page_documents: List[Document] = []

    for page_idx, page in enumerate(reader.pages):
        page_number = page_idx + 1  # 1-indexed page number for citation output
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            logger.warning(
                f"Page {page_number} in '{pdf_path}' is empty or contains no extractable text."
            )
            continue

        doc = Document(
            page_content=text,
            metadata={"page": page_number, "source": pdf_path},
        )
        page_documents.append(doc)

    if not page_documents:
        logger.error(f"No text could be extracted from PDF: '{pdf_path}'")
        raise ValueError(f"PDF at '{pdf_path}' contains no readable text content.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(page_documents)
    logger.info(
        f"Successfully parsed '{pdf_path}': Extracted {len(page_documents)} non-empty pages into {len(chunks)} text chunks."
    )
    return chunks

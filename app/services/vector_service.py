"""FAISS Vector Store service for Google Gemini embeddings and disk persistence."""

import os
import logging
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings, logger


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initializes Google Generative AI embeddings model.

    Returns:
        GoogleGenerativeAIEmbeddings: Embedding client using models/gemini-embedding-001.
    """
    if not settings.GOOGLE_API_KEY:
        logger.warning(
            "GOOGLE_API_KEY is not set. Ensure GOOGLE_API_KEY is configured in your .env file."
        )

    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def create_faiss_vector_store(
    chunks: List[Document],
    index_path: str = settings.FAISS_INDEX_PATH,
) -> FAISS:
    """Creates a FAISS vector store from document chunks and saves it to disk.

    Args:
        chunks (List[Document]): List of chunked LangChain Documents.
        index_path (str): Directory path to persist the FAISS index.

    Returns:
        FAISS: Created FAISS vector store instance.

    Raises:
        ValueError: If chunks list is empty.
    """
    if not chunks:
        raise ValueError("Cannot create vector store with an empty list of document chunks.")

    logger.info(f"Generating embeddings and building FAISS vector store for {len(chunks)} chunks...")
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Ensure parent directory exists before saving
    os.makedirs(index_path, exist_ok=True)
    vector_store.save_local(index_path)
    logger.info(f"FAISS index successfully saved to disk at '{index_path}'.")

    return vector_store


def load_faiss_vector_store(
    index_path: str = settings.FAISS_INDEX_PATH,
) -> Optional[FAISS]:
    """Safely loads a local FAISS index from disk.

    Args:
        index_path (str): Directory path where the FAISS index is stored.

    Returns:
        Optional[FAISS]: Loaded FAISS vector store instance.

    Raises:
        FileNotFoundError: If index directory does not exist.
        RuntimeError: If deserialization or file loading fails.
    """
    if not os.path.exists(index_path):
        logger.error(f"FAISS index directory not found at '{index_path}'.")
        raise FileNotFoundError(
            f"FAISS index not found at '{index_path}'. Please process a PDF to build the index first."
        )

    logger.info(f"Loading FAISS vector store from '{index_path}'...")
    embeddings = get_embeddings()
    try:
        vector_store = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info("FAISS vector store loaded successfully.")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to load FAISS index from '{index_path}': {e}")
        raise RuntimeError(f"Could not load FAISS index from '{index_path}': {e}") from e

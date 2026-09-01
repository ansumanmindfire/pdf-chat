"""LangChain RAG Chain Service combining Retriever, Gemini LLM, Citations, and ChatRepository Memory."""

import logging
from typing import Any, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings, logger
from app.database.session import SessionLocal
from app.services.vector_service import load_faiss_vector_store
from app.repositories import ChatRepository

# System instructions prompt
RAG_SYSTEM_PROMPT = """You are a helpful and precise AI assistant for answering questions based on uploaded PDF documents.

Instructions:
1. Answer the user's question strictly based on the provided Context below.
2. Consider the previous Conversation History if relevant to understand follow-up questions or pronouns (e.g. 'he', 'that project').
3. If the context does not contain enough information to answer the question, state clearly: "I cannot answer this question based on the provided PDF document."
4. Keep your answer factual, clear, and well-structured.

Context:
{context}"""


def get_llm() -> ChatGoogleGenerativeAI:
    """Initializes ChatGoogleGenerativeAI LLM client.

    Returns:
        ChatGoogleGenerativeAI: Gemini LLM instance.
    """
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )


def ask_pdf(
    question: str,
    session_id: Optional[str] = None,
    vector_store: Optional[FAISS] = None,
    index_path: str = settings.FAISS_INDEX_PATH,
    k: int = settings.K_RETRIEVAL,
) -> Dict[str, Any]:
    """Queries the FAISS vector store, includes past chat history memory if session_id is provided,
    executes LCEL RAG chain, auto-persists conversation via ChatRepository, and returns answer + citations.

    Args:
        question (str): User question string.
        session_id (Optional[str]): Database chat session ID for fetching/saving conversation memory.
        vector_store (Optional[FAISS]): Pre-loaded FAISS vector store. Loaded from index_path if None.
        index_path (str): Path to local FAISS index if vector_store is None.
        k (int): Number of top relevant document chunks to retrieve.

    Returns:
        Dict[str, Any]: Dictionary containing 'answer' (str), 'source_pages' (List[int]), and 'session_id' (Optional[str]).

    Raises:
        ValueError: If question is empty or invalid.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    chat_history: List[BaseMessage] = []
    target_index_path = index_path

    # Fetch chat history and document index path from Repository if session_id provided
    if session_id:
        with SessionLocal() as db:
            session_rec = ChatRepository.get_session_by_id(db, session_id)
            if session_rec:
                chat_history = ChatRepository.get_history_messages(db, session_id, limit=10)
                if session_rec.document and session_rec.document.faiss_index_path:
                    target_index_path = session_rec.document.faiss_index_path
            else:
                logger.warning(f"Session ID '{session_id}' not found in database. Proceeding without history.")

    # Load vector store if not provided
    if vector_store is None:
        vector_store = load_faiss_vector_store(target_index_path)

    # Retrieve top-k matching documents
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        logger.warning(f"No relevant context chunks found for question: '{question}'")
        return {
            "answer": "I could not find any relevant information in the uploaded PDF.",
            "source_pages": [],
            "session_id": session_id,
        }

    # Extract unique source page numbers
    source_pages: List[int] = sorted(
        list(
            set(
                doc.metadata.get("page")
                for doc in retrieved_docs
                if "page" in doc.metadata and doc.metadata.get("page") is not None
            )
        )
    )

    # Format context string
    context_text = "\n\n".join(
        [
            f"[Page {doc.metadata.get('page', 'Unknown')}]: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    # Construct Prompt with System, Chat History, and Question
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    llm = get_llm()
    chain = prompt | llm | StrOutputParser()

    # Invoke Chain
    logger.info(
        f"Invoking RAG chain for question: '{question}' (Session: {session_id}, History Count: {len(chat_history)})..."
    )
    answer = chain.invoke(
        {
            "context": context_text,
            "chat_history": chat_history,
            "question": question,
        }
    )

    # Persist question and answer to DB via ChatRepository if session_id exists
    if session_id:
        try:
            with SessionLocal() as db:
                ChatRepository.save_message(db, session_id, "user", question)
                ChatRepository.save_message(db, session_id, "ai", answer.strip())
        except Exception as e:
            logger.error(f"Failed to auto-save chat messages to DB for session '{session_id}': {e}")

    return {
        "answer": answer.strip(),
        "source_pages": source_pages,
        "session_id": session_id,
    }

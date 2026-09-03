"""Streamlit web application interface for PDF Chat RAG backend."""

import os
import requests
import streamlit as st

# Backend REST API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(page_title="PDF Chat")

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "filename" not in st.session_state:
    st.session_state.filename = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Backend Status & PDF Upload
with st.sidebar:
    st.title("Menu")

    # Backend Connection Check
    try:
        health_res = requests.get(f"{BACKEND_API_URL}/")
        if health_res.status_code == 200:
            st.success("Connected to RAG API")
        else:
            st.warning("RAG API returned warning")
    except requests.exceptions.RequestException:
        st.error("RAG API Offline")

    st.divider()
    st.subheader("Upload PDF")
    uploaded_file = st.file_uploader("Select a PDF file", type=["pdf"])

    if uploaded_file and st.button("Upload", use_container_width=True):
        with st.spinner("Uploading PDF and initializing session..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                res = requests.post(
                    f"{BACKEND_API_URL}/api/v1/upload",
                    files=files,
                    timeout=60,
                )

                if res.status_code == 201:
                    data = res.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.filename = data["filename"]
                    st.session_state.messages = []
                    st.success(f"Session started for '{data['filename']}'!")
                    st.rerun()
                else:
                    err_msg = res.json().get("message", res.text)
                    st.error(f"Upload failed ({res.status_code}): {err_msg}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

    if st.session_state.session_id:
        st.divider()
        st.info(f"**Document**: {st.session_state.filename}")
        if st.button("Clear Session", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.filename = None
            st.session_state.messages = []
            st.rerun()

# Main Application Interface
st.title("PDF-Chat")
st.caption("Upload a PDF & start asking questions.")

if not st.session_state.session_id:
    st.warning("Please upload a PDF file from the sidebar to start chatting.")
else:
    # Render Chat History
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "ai"
        with st.chat_message(role):
            st.write(msg["content"])
            if "pages" in msg and msg["pages"]:
                pages_str = ", ".join(str(p) for p in msg["pages"])
                st.caption(f"Cited Pages: [{pages_str}]")

    # Chat Input Prompt
    if prompt := st.chat_input("Ask question from your PDF"):
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Query Backend RAG API
        with st.chat_message("ai"):
            with st.spinner("Please wait while we generate your response"):
                try:
                    payload = {
                        "question": prompt,
                        "session_id": st.session_state.session_id,
                    }
                    chat_res = requests.post(
                        f"{BACKEND_API_URL}/api/v1/chat/",
                        json=payload,
                        timeout=45,
                    )

                    if chat_res.status_code == 200:
                        data = chat_res.json()
                        answer_text = data["answer"]
                        source_pages = data.get("source_pages", [])

                        st.write(answer_text)
                        if source_pages:
                            pages_str = ", ".join(str(p) for p in source_pages)
                            st.caption(f"Cited Pages: [{pages_str}]")

                        st.session_state.messages.append({
                            "role": "ai",
                            "content": answer_text,
                            "pages": source_pages,
                        })
                    else:
                        err_msg = chat_res.json().get("message", chat_res.text)
                        st.error(f"API Error ({chat_res.status_code}): {err_msg}")

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")

import streamlit as st
from dotenv import load_dotenv

from src.config import settings
from src.ingestion import process_uploaded_file
from src.vector_store import VectorStore
from src.rag import answer_question

load_dotenv()
st.set_page_config(page_title="AI Document Scanner", page_icon="📄", layout="wide")

@st.cache_resource
def get_store():
    return VectorStore(settings.CHROMA_DIR, settings.EMBEDDING_MODEL)

store = get_store()

st.title("📄 AI Document Scanner")
st.caption("Scan, index and chat with your documents using RAG + MCP.")

with st.sidebar:
    st.header("Document ingestion")
    uploads = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "tiff"],
        accept_multiple_files=True,
    )
    if st.button("Process documents", type="primary", disabled=not uploads):
        progress = st.progress(0)
        status = st.empty()
        added, errors = 0, []
        for i, uploaded in enumerate(uploads):
            try:
                status.write(f"Processing {uploaded.name} …")
                chunks = process_uploaded_file(uploaded.name, uploaded.getvalue())
                store.add_chunks(chunks)
                added += len(chunks)
            except Exception as exc:
                errors.append(f"{uploaded.name}: {exc}")
            progress.progress((i + 1) / len(uploads))
        status.success(f"Indexed {added} text chunks.")
        for error in errors:
            st.error(error)

    st.divider()
    st.subheader("Knowledge base")
    docs = store.list_documents()
    st.metric("Indexed documents", len(docs))
    for doc in docs:
        st.caption(f"📎 {doc}")

tab_chat, tab_search, tab_about = st.tabs(["💬 Ask documents", "🔎 Search", "ℹ️ About"])

with tab_chat:
    st.subheader("Ask a question")
    question = st.chat_input("Ask something about your uploaded documents…")
    if question:
        with st.spinner("Searching documents and generating an answer…"):
            try:
                result = answer_question(question, store)
                st.markdown(result["answer"])
                with st.expander("Retrieved source passages"):
                    for item in result["sources"]:
                        st.markdown(f"**{item['source']}** · page {item.get('page', 'N/A')}")
                        st.write(item["text"])
            except Exception as exc:
                st.error(str(exc))

with tab_search:
    query = st.text_input("Search across indexed documents")
    count = st.slider("Number of passages", 1, 10, 5)
    if st.button("Search", disabled=not query):
        for item in store.search(query, count):
            st.markdown(f"**{item['source']}** · page {item.get('page', 'N/A')}")
            st.write(item["text"])
            st.divider()

with tab_about:
    st.markdown("""
    **How it works**
    1. Extract text from PDFs, Word documents, text files and images.
    2. OCR image-based/scanned pages when Tesseract is installed.
    3. Split extracted text into overlapping chunks.
    4. Embed chunks and persist them in ChromaDB.
    5. Retrieve relevant passages and ask the configured LLM to answer from them.

    The MCP server exposes the same indexed knowledge base to MCP-compatible clients.
    """)

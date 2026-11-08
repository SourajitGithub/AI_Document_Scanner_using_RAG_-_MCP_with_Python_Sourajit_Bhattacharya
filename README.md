# AI Document Scanner — RAG + MCP + Streamlit

A local-first document intelligence starter project. Upload PDF, DOCX, TXT and image files,
extract text (OCR for scanned PDFs/images), index chunks in ChromaDB, and query them with RAG.
An MCP server exposes the same knowledge base to MCP-compatible clients.

## Features

- Streamlit document upload and chat interface
- PDF and DOCX text extraction
- OCR for scanned PDF pages and image files (Tesseract)
- Overlapping text chunking
- Sentence Transformer embeddings
- Persistent ChromaDB vector store
- OpenAI-powered RAG answers with source/page references
- MCP tools: `search_documents`, `list_documents`, `document_index_stats`

## 1. Prerequisites

- Python 3.10 or newer
- An OpenAI API key for generated RAG answers
- Tesseract OCR installed on the operating system for image/scanned-page OCR

### Install Tesseract

- Windows: install the Tesseract OCR application and add its installation folder to PATH.
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

OCR is optional for text-based PDFs, DOCX and TXT files.

## 2. Setup

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

## 3. Run Streamlit

From the project root:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501.
Upload files in the sidebar and click **Process documents**. Then ask questions in the
**Ask documents** tab.

The first run downloads the Sentence Transformers embedding model. This can take a few minutes.

## 4. Run the MCP server

In a second terminal, activate the same virtual environment and run:

```bash
python mcp_server.py
```

The server uses stdio transport by default. Configure your MCP-compatible client to launch
this script using the Python executable from this project's virtual environment, with the
project root as its working directory.

Example MCP client configuration (adjust the absolute paths):

```json
{
  "mcpServers": {
    "ai-document-scanner": {
      "command": "C:/path/to/project/.venv/Scripts/python.exe",
      "args": ["C:/path/to/project/mcp_server.py"]
    }
  }
}
```

The MCP server exposes:
- `search_documents(query, top_k)` — semantic search with source/page metadata
- `list_documents()` — indexed filenames
- `document_index_stats()` — document and chunk counts

The Streamlit app and MCP server must point to the same `CHROMA_DIR` and
`COLLECTION_NAME`.

## 5. Project structure

```text
ai_document_scanner/
├── app.py                 # Streamlit user interface
├── mcp_server.py          # MCP server and tools
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py           # Environment configuration
│   ├── chunking.py         # Text chunking
│   ├── ingestion.py        # PDF/DOCX/TXT/image extraction + OCR
│   ├── vector_store.py     # Embeddings + ChromaDB
│   └── rag.py              # Retrieval-augmented generation
├── tests/
│   └── test_chunking.py
└── data/
    └── chroma/             # Created automatically; not committed
```

## 6. Data flow

1. User uploads a document through Streamlit.
2. `ingestion.py` extracts text and applies OCR when required.
3. `chunking.py` creates overlapping chunks.
4. `vector_store.py` embeds and upserts chunks into ChromaDB.
5. `rag.py` retrieves the most relevant chunks and sends them to the LLM.
6. The answer includes source/page references and the UI shows retrieved passages.
7. MCP clients can independently call the knowledge-base tools.

## 7. Run tests

```bash
pytest -q
```

## 8. Important implementation notes

- Documents and embeddings are stored locally in `data/chroma`.
- The OpenAI API receives the retrieved text passages when a question is answered.
  Do not index confidential documents unless your organization's data policy permits it.
- OCR quality depends on scan resolution, language packs, rotation and document quality.
- This starter version indexes uploaded files but does not yet implement user accounts,
  per-user access control, document deletion UI, malware scanning or production deployment.
- For production, add authentication, upload scanning, audit logging, tenant isolation,
  rate limits, backups and explicit document-retention controls.
- Avoid exposing the MCP server to an untrusted network without authentication and transport security.

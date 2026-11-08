"""MCP tools for searching and inspecting the local document knowledge base."""
from mcp.server.fastmcp import FastMCP
from src.vector_store import VectorStore
from src.config import settings

mcp = FastMCP("AI Document Scanner")
store = VectorStore(settings.CHROMA_DIR, settings.EMBEDDING_MODEL)

@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> list[dict]:
    """Search indexed document passages by semantic similarity."""
    return store.search(query, top_k)

@mcp.tool()
def list_documents() -> list[str]:
    """List filenames currently indexed in the document knowledge base."""
    return store.list_documents()

@mcp.tool()
def document_index_stats() -> dict:
    """Return the number of indexed chunks and distinct source documents."""
    docs = store.list_documents()
    return {"document_count": len(docs), "chunk_count": store.count(), "documents": docs}

if __name__ == "__main__":
    mcp.run()

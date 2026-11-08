from typing import Dict, List
import chromadb
from sentence_transformers import SentenceTransformer

from src.config import settings

class VectorStore:
    def __init__(self, persist_dir: str = None, embedding_model: str = None):
        self.client = chromadb.PersistentClient(path=persist_dir or settings.CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = SentenceTransformer(embedding_model or settings.EMBEDDING_MODEL)

    def add_chunks(self, chunks: List[Dict]) -> None:
        if not chunks:
            return
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.encode(texts, normalize_embeddings=True).tolist()
        self.collection.upsert(
            ids=[c["id"] for c in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[{
                "source": c["source"],
                "page": int(c["page"]),
                "chunk": int(c["chunk"]),
            } for c in chunks],
        )

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        vector = self.embedder.encode([query], normalize_embeddings=True).tolist()
        result = self.collection.query(
            query_embeddings=vector,
            n_results=max(1, top_k or settings.TOP_K),
            include=["documents", "metadatas", "distances"],
        )
        items = []
        if not result["ids"] or not result["ids"][0]:
            return items
        for doc, meta, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            items.append({
                "text": doc,
                "source": meta.get("source", "Unknown"),
                "page": meta.get("page"),
                "chunk": meta.get("chunk"),
                "distance": distance,
            })
        return items

    def list_documents(self) -> List[str]:
        records = self.collection.get(include=["metadatas"])
        names = {m.get("source", "Unknown") for m in records.get("metadatas", [])}
        return sorted(names)

    def count(self) -> int:
        return self.collection.count()

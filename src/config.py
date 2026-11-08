
import os
from pathlib import Path
from dotenv import load_dotenv

# Define project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from project root .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:

    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.5-flash-lite"
    )

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # ChromaDB Configuration
    CHROMA_DIR = os.getenv(
        "CHROMA_DIR",
        str(BASE_DIR / "data" / "chroma")
    )

    COLLECTION_NAME = os.getenv(
        "COLLECTION_NAME",
        "documents"
    )

    # Text Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))

    CHUNK_OVERLAP = int(
        os.getenv("CHUNK_OVERLAP", "150")
    )

    # RAG Configuration
    TOP_K = int(os.getenv("TOP_K", "5"))

    # File Upload Configuration
    MAX_UPLOAD_MB = int(
        os.getenv("MAX_UPLOAD_MB", "25")
    )


# Initialize settings
settings = Settings()

# Create ChromaDB directory if it does not exist
Path(settings.CHROMA_DIR).mkdir(
    parents=True,
    exist_ok=True
)

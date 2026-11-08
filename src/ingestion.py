import io
import hashlib
from pathlib import Path
from typing import Dict, List
from docx import Document
from PIL import Image
import pymupdf
from src.chunking import split_text
from src.config import settings

def _ocr_image(image: Image.Image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(image)
    except ImportError as exc:
        raise RuntimeError(
            "OCR requires pytesseract and the Tesseract application. "
            "Install both, or use a text-based PDF."
        ) from exc


def extract_pdf(data: bytes) -> List[Dict]:
    pages = []

    with pymupdf.open(stream=data, filetype="pdf") as pdf:

        for page_no, page in enumerate(pdf, start=1):

            text = page.get_text("text").strip()

            if len(text) < 30:

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                text = _ocr_image(image).strip()

            if text:
                pages.append({
                    "page": page_no,
                    "text": text
                })

    return pages


def extract_document(filename: str, data: bytes) -> List[Dict]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_pdf(data)
    if ext == ".docx":
        doc = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [{"page": 1, "text": text}] if text else []
    if ext == ".txt":
        text = data.decode("utf-8", errors="replace")
        return [{"page": 1, "text": text}] if text.strip() else []
    if ext in {".png", ".jpg", ".jpeg", ".tiff"}:
        image = Image.open(io.BytesIO(data)).convert("RGB")
        text = _ocr_image(image).strip()
        return [{"page": 1, "text": text}] if text else []
    raise ValueError(f"Unsupported file type: {ext}")

def process_uploaded_file(filename: str, data: bytes) -> List[Dict]:
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"File exceeds {settings.MAX_UPLOAD_MB} MB limit.")
    pages = extract_document(filename, data)
    chunks = []
    for page in pages:
        for index, chunk in enumerate(
            split_text(page["text"], settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        ):
            stable = hashlib.sha256(
                f"{filename}:{page['page']}:{index}:{chunk}".encode("utf-8")
            ).hexdigest()
            chunks.append({
                "id": stable,
                "text": chunk,
                "source": filename,
                "page": page["page"],
                "chunk": index,
            })
    if not chunks:
        raise ValueError("No text could be extracted from this file.")
    return chunks

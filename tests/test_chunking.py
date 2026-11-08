import pytest
from src.chunking import split_text

def test_empty_text():
    assert split_text("") == []

def test_chunks_cover_text():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = split_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(chunks)

def test_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("hello", chunk_size=10, overlap=10)

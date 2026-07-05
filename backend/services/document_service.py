"""
Document Processing Module (Sections 3.5.4 and 4.10 of the dissertation).

Responsible for:
    1. Reading an uploaded document (PDF, DOCX, or TXT)
    2. Extracting and cleaning its textual content
    3. Splitting the content into overlapping chunks for embedding
"""
import os
import re
from pypdf import PdfReader
import docx


def extract_text(file_path: str, file_type: str) -> str:
    """Extract raw text from a PDF, DOCX, or TXT file."""
    file_type = file_type.lower()

    if file_type == "pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_type == "docx":
        document = docx.Document(file_path)
        return "\n".join(p.text for p in document.paragraphs)

    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {file_type}")


def clean_text(raw_text: str) -> str:
    """Remove excess whitespace and normalize the extracted text."""
    text = re.sub(r"\s+", " ", raw_text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """
    Split cleaned text into overlapping word-based chunks.

    Chunking improves retrieval accuracy because the semantic search
    module can retrieve only the relevant portion of a document instead
    of the entire file (Section 3.5.4).
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def process_document(file_path: str, file_type: str) -> list[str]:
    """Full pipeline: extract -> clean -> chunk. Returns list of text chunks."""
    raw_text = extract_text(file_path, file_type)
    cleaned = clean_text(raw_text)
    return chunk_text(cleaned)


def get_file_type(filename: str) -> str:
    """Infer the document type from its file extension."""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext in ("pdf", "docx", "txt"):
        return ext
    raise ValueError(f"Unsupported file extension: {ext}")

import os
from pathlib import Path
from typing import Iterable, List, Tuple

from pypdf import PdfReader

from app.core.config import DOCUMENTS_DIR
from app.services.vector_store import get_documents_collection


def extract_text_from_pdf(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text from all pages of a PDF.

    Returns a list of (page_number, text) tuples. Page numbers are 1-based.
    """
    reader = PdfReader(str(pdf_path))
    pages: List[Tuple[int, str]] = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue
        pages.append((idx + 1, text))
    return pages


def chunk_text(
    text: str,
    max_chars: int = 1000,
    overlap: int = 200,
) -> List[str]:
    """
    Simple character-based chunking with overlap.
    """
    chunks: List[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def iter_pdf_files(folder: Path) -> Iterable[Path]:
    for root, _, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(".pdf"):
                yield Path(root) / name


def ingest_pdfs_in_folder(folder: Path | None = None) -> None:
    """
    Walk the given folder (or DOCUMENTS_DIR by default), extract text from each
    PDF, chunk it, and store it in ChromaDB.
    """
    if folder is None:
        folder = Path(DOCUMENTS_DIR)

    folder = folder.resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Documents folder does not exist: {folder}")

    collection = get_documents_collection()

    for pdf_path in iter_pdf_files(folder):
        pdf_path = pdf_path.resolve()
        print(f"Ingesting: {pdf_path}")

        # Remove existing entries for this file so re-runs stay clean
        collection.delete(where={"source": str(pdf_path)})

        pages = extract_text_from_pdf(pdf_path)
        if not pages:
            print(f"  -> No extractable text, skipping.")
            continue

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[dict] = []

        for page_number, page_text in pages:
            chunks = chunk_text(page_text)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{pdf_path}::page_{page_number}::chunk_{chunk_idx}"
                ids.append(doc_id)
                documents.append(chunk)
                metadatas.append(
                    {
                        "source": str(pdf_path),
                        "page": page_number,
                        "chunk": chunk_idx,
                    }
                )

        if documents:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            print(f"  -> Stored {len(documents)} chunks.")


if __name__ == "__main__":
    ingest_pdfs_in_folder()


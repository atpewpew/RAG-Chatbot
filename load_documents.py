import os
import io
import shutil
from pathlib import Path
from functools import lru_cache
from typing import Dict, List
import streamlit as st
import pdfplumber
import docx
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import fitz
from PIL import Image
import pytesseract

@st.cache_resource
def _load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = _load_model()

# Initialize FAISS Index
dimension = 384  # Embedding size for all-MiniLM-L6-v2
index = faiss.IndexFlatL2(dimension)
documents: List[str] = []

# OCR is used only when a page has little/no extractable text
_OCR_MIN_TEXT_CHARS = 20

# Keywords that indicate a broad/whole-document query
_BROAD_KEYWORDS = {
    "summarize", "summary", "overview", "brief", "whole", "entire",
    "all", "everything", "main points", "key points", "what is this",
    "what does this", "describe", "about", "explain",
}

def _is_broad_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _BROAD_KEYWORDS)

def _chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks of ~chunk_size words with ~overlap word overlap."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]

def _needs_ocr(text: str) -> bool:
    return len(text.strip()) < _OCR_MIN_TEXT_CHARS

@lru_cache(maxsize=1)
def _resolve_tesseract_cmd() -> str | None:
    path_candidate = shutil.which("tesseract")
    if path_candidate:
        return path_candidate

    env_candidate = os.getenv("TESSERACT_CMD")
    if env_candidate and Path(env_candidate).exists():
        return env_candidate

    windows_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for candidate in windows_candidates:
        if Path(candidate).exists():
            return candidate

    return None

def _is_tesseract_available() -> bool:
    return _resolve_tesseract_cmd() is not None

def _warn_ocr_unavailable_once() -> None:
    if _is_tesseract_available():
        return
    if not st.session_state.get("ocr_unavailable_warned", False):
        st.warning(
            "OCR is unavailable because the Tesseract binary is not installed. "
            "Text-based extraction still works; install Tesseract to enable OCR for scanned PDFs/images."
        )
        st.session_state["ocr_unavailable_warned"] = True

def _ocr_image(image: Image.Image) -> str:
    cmd = _resolve_tesseract_cmd()
    if not cmd:
        _warn_ocr_unavailable_once()
        return ""
    pytesseract.pytesseract.tesseract_cmd = cmd
    return pytesseract.image_to_string(image).strip()

def _ocr_pdf_pages(file_path: str, page_indices: List[int]) -> Dict[int, str]:
    results: Dict[int, str] = {}
    if not page_indices:
        return results
    if not _is_tesseract_available():
        _warn_ocr_unavailable_once()
        return results

    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        st.warning(f"OCR could not open PDF pages: {exc}")
        return results

    try:
        for page_index in page_indices:
            try:
                page = doc.load_page(page_index)
                # 2x scale improves OCR quality without excessive memory use.
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                ocr_text = _ocr_image(image)
                if ocr_text:
                    results[page_index] = ocr_text
            except Exception as exc:
                st.warning(f"OCR failed on PDF page {page_index + 1}: {exc}")
    finally:
        doc.close()

    return results

def load_txt(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return _chunk_text(text)

def load_pdf(file_path: str) -> List[str]:
    page_texts: List[str] = []
    ocr_page_indices: List[int] = []

    with pdfplumber.open(file_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            if _needs_ocr(text):
                ocr_page_indices.append(idx)
                page_texts.append("")
            else:
                page_texts.append(text)

    if ocr_page_indices:
        ocr_results = _ocr_pdf_pages(file_path, ocr_page_indices)
        for idx, ocr_text in ocr_results.items():
            page_texts[idx] = ocr_text

    merged_text = "\n".join(text for text in page_texts if text.strip())
    if not merged_text:
        st.warning("No readable text found in this PDF (including OCR fallback).")
    return _chunk_text(merged_text)

def load_docx(file_path: str) -> List[str]:
    doc = docx.Document(file_path)
    text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    return _chunk_text(text)

def load_xlsx(file_path: str) -> List[str]:
    df = pd.read_excel(file_path)
    cells = []
    for column in df.columns:
        cells.extend([str(cell).strip() for cell in df[column] if pd.notnull(cell)])
    return _chunk_text(" ".join(cells))

def load_image(file_path: str) -> List[str]:
    try:
        with Image.open(file_path) as image:
            text = _ocr_image(image.convert("RGB"))
    except Exception as exc:
        st.warning(f"Unable to OCR image file: {exc}")
        return []

    if not text:
        st.warning("No readable text found in this image.")
    return _chunk_text(text)

def load_documents(file_path: str):
    global documents
    file_extension = os.path.splitext(file_path)[-1].lower()
    if file_extension == ".txt":
        documents.extend(load_txt(file_path))
    elif file_extension == ".pdf":
        documents.extend(load_pdf(file_path))
    elif file_extension == ".docx":
        documents.extend(load_docx(file_path))
    elif file_extension == ".xlsx":
        documents.extend(load_xlsx(file_path))
    elif file_extension in {".png", ".jpg", ".jpeg"}:
        documents.extend(load_image(file_path))
    else:
        st.warning(f"Unsupported file type: {file_extension}")

def add_documents_to_index():
    global documents
    if not documents:
        return
    embeddings = model.encode(documents)
    index.add(np.array(embeddings, dtype=np.float32))

def reset_documents_index() -> None:
    global index, documents
    index = faiss.IndexFlatL2(dimension)
    documents = []

def retrieve_relevant_documents(query, top_k=15):
    if not documents:
        return []
    # Broad/summary queries get more chunks for better coverage
    effective_k = min(len(documents), 30 if _is_broad_query(query) else top_k)
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), effective_k)
    return [documents[idx] for idx in indices[0] if 0 <= idx < len(documents)]
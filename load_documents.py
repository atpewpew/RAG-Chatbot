import os
import streamlit as st
import pdfplumber
import docx
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS Index
dimension = 384  # Embedding size for all-MiniLM-L6-v2
index = faiss.IndexFlatL2(dimension)
documents = []

# Keywords that indicate a broad/whole-document query
_BROAD_KEYWORDS = {
    "summarize", "summary", "overview", "brief", "whole", "entire",
    "all", "everything", "main points", "key points", "what is this",
    "what does this", "describe", "about", "explain",
}

def _is_broad_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _BROAD_KEYWORDS)

def _chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
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

def load_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return _chunk_text(text)

def load_pdf(file_path):
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return _chunk_text("\n".join(pages))

def load_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    return _chunk_text(text)

def load_xlsx(file_path):
    df = pd.read_excel(file_path)
    cells = []
    for column in df.columns:
        cells.extend([str(cell).strip() for cell in df[column] if pd.notnull(cell)])
    return _chunk_text(" ".join(cells))

def load_documents(file_path):
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
    else:
        st.warning(f"Unsupported file type: {file_extension}")

def add_documents_to_index():
    global documents
    embeddings = model.encode(documents)
    index.add(np.array(embeddings, dtype=np.float32))

def retrieve_relevant_documents(query, top_k=15):
    if not documents:
        return []
    # Broad/summary queries get more chunks for better coverage
    effective_k = min(len(documents), 30 if _is_broad_query(query) else top_k)
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), effective_k)
    return [documents[idx] for idx in indices[0] if 0 <= idx < len(documents)]
# RAG Document Q&A ChatBot

A **Retrieval-Augmented Generation (RAG)** chatbot built with Streamlit. Upload documents, ask questions, and get accurate, context-grounded answers powered by Google Gemini.

---

## Features

- **Multi-format document support** — `.txt`, `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.jpeg`
- **OCR fallback for scanned PDFs** — pages with little or no extractable text are OCR'd automatically
- **Image OCR support** — image files are ingested through OCR and added to the same RAG pipeline
- **Smart chunking** — documents are split into 300-word overlapping chunks for better context coverage
- **Semantic search** — FAISS vector index with `all-MiniLM-L6-v2` embeddings for fast, relevant retrieval
- **Broad query detection** — summary/overview queries automatically retrieve more chunks for full-document coverage
- **Conversational memory** — full chat history displayed in the UI across the session
- **No duplicate indexing** — re-uploading the same file in a session is safely skipped
- **Docker ready** — single `docker run` command to deploy anywhere

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini (`gemini-3.1-flash-lite-preview`) via `google-genai` SDK |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector store | FAISS (`faiss-cpu`) |
| PDF parsing | `pdfplumber` |
| OCR | `pytesseract` + Tesseract OCR engine |
| PDF page rendering for OCR fallback | `PyMuPDF` |
| Docx parsing | `python-docx` |
| Excel parsing | `pandas` |
| Containerization | Docker |

---

## Project Structure

```
├── app.py                # Streamlit UI and session management
├── load_documents.py     # Document loading, chunking, FAISS indexing and retrieval
├── gemini.py             # Google Gemini client and response generation
├── utils.py              # Environment variable loader
├── requirements.txt      # Python dependencies
├── packages.txt          # Streamlit Cloud OS packages (Tesseract)
├── Dockerfile            # Container build definition
├── .dockerignore         # Files excluded from Docker build context
├── .gitignore            # Files excluded from git
└── .env                  # API keys (never committed)
```

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/atpewpew/RAG-Chatbot.git
cd RAG-Chatbot
```

### 2. Create a `.env` file
```bash
echo GEMINI_API_KEY=your_api_key_here > .env
```
Get a free API key at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 3.1 Install Tesseract OCR (required for OCR features)

`pytesseract` requires the Tesseract OCR binary to be installed on your system.

- Windows: install from the official UB Mannheim build or Tesseract installer, then ensure `tesseract` is in your `PATH`.
- Linux (Debian/Ubuntu): `sudo apt-get install tesseract-ocr tesseract-ocr-eng`
- macOS (Homebrew): `brew install tesseract`

Troubleshooting (Windows): if `tesseract --version` works in Command Prompt but OCR still shows unavailable in Streamlit, restart the terminal/IDE and rerun the app. You can also set an explicit path with environment variable `TESSERACT_CMD` (example: `C:\Program Files\Tesseract-OCR\tesseract.exe`).

### 4. Run the app
```bash
python -m streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Docker Setup

### Build the image
```bash
docker build -t rag-doc-bot .
```

### Run the container
```bash
docker run -p 8501:8501 -e GEMINI_API_KEY=your_api_key_here rag-doc-bot
```

Open **http://localhost:8501** in your browser.

> The API key is passed at runtime via `-e` and is never baked into the image.

---

## Streamlit Cloud Notes

- This repo includes `packages.txt` so Streamlit Cloud installs required OCR OS packages.
- `packages.txt` currently installs: `tesseract-ocr`, `tesseract-ocr-eng`.
- Keep `GEMINI_API_KEY` in Streamlit Cloud Secrets.
- If Tesseract is unavailable at runtime, the app shows a warning and continues with text-based extraction.

---

## Usage

1. **Upload documents** using the sidebar — supported formats: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.jpeg`
2. **Ask questions** in the chat input — the bot retrieves the most relevant chunks and generates a grounded answer
3. For scanned/image-based PDFs, each page first uses normal text extraction, and OCR runs only on pages with little/no text
4. For broad questions like *"summarize this document"* or *"what are the main points?"*, the retrieval automatically widens to cover more of the document
5. Use **Clear Chat** to reset the conversation without re-uploading files

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

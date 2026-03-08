# RAG Document Q&A ChatBot

A **Retrieval-Augmented Generation (RAG)** chatbot built with Streamlit. Upload documents, ask questions, and get accurate, context-grounded answers powered by Google Gemini.

---

## Features

- **Multi-format document support** — `.txt`, `.pdf`, `.docx`, `.xlsx`
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

## Usage

1. **Upload documents** using the sidebar — supported formats: `.txt`, `.pdf`, `.docx`, `.xlsx`
2. **Ask questions** in the chat input — the bot retrieves the most relevant chunks and generates a grounded answer
3. For broad questions like *"summarize this document"* or *"what are the main points?"*, the retrieval automatically widens to cover more of the document
4. Use **Clear Chat** to reset the conversation without re-uploading files

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request


This project is a **Retrieval-Augmented Generation (RAG)**-based chatbot built with **Streamlit**. It allows users to upload documents, ask queries, and receive context-aware responses from the document data.

---

## 🚀 **Features**

- **Document Upload**: Supports `.txt`, `.pdf`, `.docx`, and `.xlsx` file uploads.
- **Intelligent Responses**: Answers queries using **retrieved document content** and a conversational context.
- **Interactive UI**: A clean and user-friendly interface with a modern dark theme.
- **Chat History**: Maintains query and response history for a seamless conversation.

---

## 🛠️ **Technologies Used**

- **Python**: Backend logic for processing and retrieving document content.
- **Streamlit**: Framework for the web interface.
- **Custom Libraries**:  
   - `load_documents.py`: Loads and processes uploaded documents.  
   - `gemini.py`: Handles the generation of responses using the RAG approach.  
   - `utils.py`: Manages helper functions like environment setup.  

---

## 📂 **Project Structure**

```
📁 RAG-Based-Document-Chatbot/
│
├── app.py                 # Main Streamlit app
├── load_documents.py      # Document upload and processing logic
├── gemini.py              # Response generation logic
├── utils.py               # Utility functions and environment loader
├── temp/                  # Temporary storage for uploaded files
├── requirements.txt       # Project dependencies
└── README.md              # Documentation (this file)
```

---

## 💻 **Installation and Setup**

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/rag-document-chatbot
cd rag-document-chatbot
```

### 2. Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit app:
```bash
streamlit run app.py
```

### 4. Access the Application
Open your browser and navigate to:  
**`http://localhost:8501`**

---

## 🎯 **Usage**

1. **Upload Documents**:  
   - Use the sidebar to upload `.txt`, `.pdf`, `.docx`, or `.xlsx` files.  
   - Uploaded documents will be processed and indexed automatically.

2. **Ask Queries**:  
   - Enter your question or query in the chatbox.  
   - The chatbot will retrieve relevant information from the documents and generate a response.

3. **View Responses**:  
   - Responses are generated in real-time and displayed under the chat interface.  

---

## 🥩 **Future Enhancements**

- Integrate advanced language models for better responses.  
- Support for more file formats.  
- Add a downloadable chat transcript feature.  
- Multi-user authentication for secure access.  

---

## 🤝 **Contributions**

Contributions are welcome! Follow these steps:  
1. **Fork** the repository.  
2. **Create a new branch**:  
   ```bash
   git checkout -b feature-branch
   ```
3. **Make your changes** and commit:  
   ```bash
   git commit -m "Add new feature"
   ```
4. **Push** to your branch:  
   ```bash
   git push origin feature-branch
   ```
5. Submit a **Pull Request**.




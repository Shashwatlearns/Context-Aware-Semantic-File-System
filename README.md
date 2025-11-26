# 🌐 Context-Aware Semantic File System (NeuroDrive)

**NeuroDrive** is an **AI-powered local file system** that understands the *meaning* of your files and allows **semantic search**, **context-aware ranking**, and **natural language queries**.

Instead of searching by filenames or folders, you can simply ask:
- “Show my machine learning notes.”
- “Find the PDF where I wrote bubble sort.”
- “Where is my chemistry assignment about reactions?”

The system processes documents, extracts text, generates embeddings, stores them in a vector database, and returns the most relevant files with contextual ranking.

---

## 🚀 Features

- Semantic file search (meaning-based)
- Natural language query support
- Context-aware ranking (recency, type, topic)
- AI embeddings using Sentence Transformers
- Vector similarity search using FAISS
- PDF/DOCX/TXT extraction
- Simple Streamlit UI
- Everything runs **offline** on your computer

---

## 🧠 Tech Stack

### AI & Processing
- Python
- SentenceTransformers
- FAISS (Facebook AI Similarity Search)

### Backend
- FastAPI
- Pydantic
- Uvicorn

### File Processing
- PyPDF
- python-docx

### Frontend
- Streamlit

---

## 📂 Project Structure

```
Context-Aware-Semantic-File-System/
│
├── backend/
│   ├── main.py
│   ├── file_scanner/
│   │   └── scanner.py
│   ├── extraction/
│   │   ├── pdf_extractor.py
│   │   ├── docx_extractor.py
│   │   ├── txt_extractor.py
│   │   └── extraction_manager.py
│   ├── embeddings/
│   │   └── embedder.py
│   ├── vector_db/
│   │   └── faiss_db.py
│   └── context_engine/
│       ├── context_builder.py
│       └── ranking.py
│
├── frontend/
│   ├── app.py
│   └── components/
│
├── data/
│   ├── sample_files/
│   └── indexes/
│
└── docs/
    ├── ppt/
    └── diagrams/
```

---

## 👥 Team Members & Roles

| Member      | Responsibility                        |
|-------------|---------------------------------------|
| **Shaunak**| Backend API (FastAPI), integration    |
| **Shashwat**| File scanner & text extraction        |
| **Pavan**| Embeddings + FAISS vector DB          |
| **Manvi**| Context engine + ranking              |
| **Tanmay**| Frontend UI (Streamlit), documentation|

---

## 🔀 Branching Strategy

```
main → Final stable version
dev  → Integration branch

backend-api          → Member 1
file-scanner         → Member 2
embeddings-vector-db → Member 3
context-engine       → Member 4
frontend-ui          → Member 5
```

Each member works only in their assigned branch and submits Pull Requests into `dev`.

---

## 🛠️ How It Works

1. User selects folder
2. File scanner reads all file paths & metadata
3. Extractors read content (PDF/DOCX/TXT)
4. Embedding model converts text → vectors
5. Vectors are stored in FAISS
6. User enters a natural query
7. Query is converted to a vector
8. FAISS finds closest matching files
9. Context engine re-ranks results
10. UI displays ranked results and previews

---

## 📌 Current Progress (20% Stage)

- Repository and structure created
- File scanning module added
- PDF/DOCX/TXT extraction working
- Embedding model loaded successfully
- FAISS index created for sample files
- Basic FastAPI backend setup
- UI skeleton (Streamlit) prepared

---

## 🧪 Next Steps

- Full indexing pipeline (scan → extract → embed → store)
- Full search pipeline (query → embed → match → rank)
- Integration of all modules via FastAPI
- Connect frontend to backend
- Final UI polish and documentation

---

## 📜 License
This project is licensed under the MIT License.

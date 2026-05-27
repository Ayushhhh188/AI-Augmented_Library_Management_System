# CC Library System — RAG-Powered Document Management

A full-stack library document management system with an integrated AI chatbot powered by Retrieval-Augmented Generation (RAG). Upload documents, search the library catalog, and ask questions about document contents — all through a clean web interface with Google OAuth authentication.

## Project Live at:
https://ai-augmented-library-management-system-1.onrender.com

---

## Features

- **Google OAuth Login** — Secure authentication via Google, no passwords to manage
- **Document Upload & Ingestion** — Upload PDF, DOCX, or TXT files; they are automatically chunked and ingested into the vector database for AI querying
- **RAG Chatbot** — Ask natural language questions about uploaded documents; answers are grounded strictly in document content using ChromaDB + Gemini
- **Library Search** — Search documents by title with case-insensitive partial matching
- **Recent Documents** — Browse the 10 most recently added documents
- **Admin Panel** — Manage users (admin role required)
- **Docker Support** — Fully containerized with `docker-compose` for one-command deployment

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Flask Web App                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────┐  │
│  │ Google OAuth │  │ MongoDB Atlas │  │  Upload  │  │
│  │   Auth Flow  │  │  (metadata)   │  │  /static │  │
│  └──────────────┘  └───────────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    RAG Pipeline      │
              │                      │
              │  Query → Embed →     │
              │  ChromaDB Search →   │
              │  Gemini LLM →        │
              │  Answer              │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ChromaDB         Sentence        Gemini API
  (vector_db/)   Transformers    (gemini-3.5-flash)
                (all-MiniLM-L6)
```

### Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask |
| Authentication | Google OAuth 2.0 via Authlib |
| Database | MongoDB Atlas (document metadata) |
| Vector Store | ChromaDB (persistent, local) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| LLM | Google Gemini 2.0 Flash (`google-genai` SDK) |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
cc_library_system_rag/
│
├── app.py                  # Main Flask application, all routes
│
├── chatbot/                # RAG pipeline modules
│   ├── document_loader.py  # Loads PDF, DOCX, TXT from uploads folder
│   ├── chunking.py         # Splits text into overlapping chunks
│   ├── embeddings.py       # Sentence-transformer embedding wrapper
│   ├── vector.py           # ChromaDB read/write operations
│   ├── rag_pipeline.py     # Orchestrates retrieval + LLM generation
│   ├── prompts.py          # Prompt template for the LLM
│   ├── llm.py              # Gemini API call via google-genai SDK
│   └── reranker.py         # Placeholder for future reranking logic
│
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── images/
│   └── uploads/            # Uploaded documents stored here
│
├── vector_db/              # ChromaDB persistent storage
├── tests/                  # Test files
│
├── ingest.py               # Standalone script to bulk-ingest documents
├── keep_alive.py           # Pings app + MongoDB to prevent inactivity pauses
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── .env                    # Environment variables (not committed)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- A [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account (free M0 tier works)
- A [Google Cloud](https://console.cloud.google.com/) project with OAuth 2.0 credentials
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (free tier works)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/cc-library-system-rag.git
cd cc-library-system-rag
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_flask_secret_key_here

# MongoDB Atlas
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# For keep_alive.py
APP_URL=http://localhost:5000
```

### 3a. Run Locally (with venv)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python app.py
```

### 3b. Run with Docker

```bash
docker-compose up --build
```

The app will be available at `http://localhost:5000`.

> **Note:** Uploaded files and the vector database are persisted via Docker volumes so they survive container restarts.

---

## How the RAG Pipeline Works

1. **Upload** — A user uploads a PDF/DOCX/TXT file via the web UI
2. **Load** — `document_loader.py` reads the file content from disk
3. **Chunk** — `chunking.py` splits the text into 1200-character chunks with 200-character overlap using LangChain's `RecursiveCharacterTextSplitter`
4. **Embed** — `embeddings.py` converts each chunk into a vector using `all-MiniLM-L6-v2`
5. **Store** — `vector.py` saves the embeddings + text to ChromaDB under the `library_documents` collection
6. **Query** — When a user asks a question in the chatbot, the question is embedded and ChromaDB returns the top 8 most similar chunks
7. **Generate** — The top 5 unique chunks are assembled into a context window and passed to Gemini 2.0 Flash with a strict grounding prompt
8. **Answer** — The LLM returns a concise, factual answer based only on the retrieved context

---

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an **OAuth 2.0 Client ID** (Web application type)
3. Add `http://localhost:5000/auth/callback` to **Authorized redirect URIs**
4. Copy the Client ID and Client Secret into your `.env`

---

##  MongoDB Atlas Setup

1. Create a free M0 cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a database user and whitelist your IP (or use `0.0.0.0/0` for Docker)
3. Copy the connection string into `MONGO_URI` in `.env`
4. The app auto-creates two collections: `users` and `documents`

---

## Docker Notes

The `docker-compose.yml` mounts two local directories as volumes:

```yaml
volumes:
  - ./static/uploads:/app/static/uploads   # uploaded files
  - ./vector_db:/app/vector_db             # ChromaDB data
```

This means your documents and embeddings persist even if you rebuild the container. To do a full fresh start:

```bash
docker-compose down
rm -rf static/uploads/* vector_db/*
docker-compose up --build
```

---

##  Keeping Services Active (Free Tier)

If you're hosting on a free-tier platform like [Render](https://render.com), services can spin down after inactivity. Run `keep_alive.py` to prevent this:

```bash
python keep_alive.py
```

This pings your app URL and MongoDB every 10 minutes. For production, consider running it as a background service or using [UptimeRobot](https://uptimerobot.com) (free) to monitor and keep your app awake.

---

## Bulk Ingestion

To ingest all documents already in `static/uploads/` into the vector database at once (useful after first setup or a fresh vector DB):

```bash
python ingest.py
```

---

## User Roles

| Role | Access |
|---|---|
| `user` | Login, search, upload, manage own files, use chatbot |
| `admin` | All of the above + access to `/admin/users` panel |

Roles are assigned in MongoDB. To make yourself an admin, update your user document in Atlas:

```json
{ "$set": { "role": "admin" } }
```

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session secret key |
| `MONGO_URI` | MongoDB Atlas connection string |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `APP_URL` | Your deployed app URL (for keep_alive.py) |

---

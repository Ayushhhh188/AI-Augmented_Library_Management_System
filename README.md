# Central Coalfields Limited AI-Augmented Library Management System

## Overview

The Central Coalfields Limited AI-Augmented Library Management System is a full-stack enterprise document management and retrieval platform developed as an internship project. The system combines traditional CRUD-based digital library operations with modern Retrieval-Augmented Generation (RAG) architecture powered by local Small Language Models (SLMs), vector databases, semantic search, and AI-assisted document querying.

![image alt](https://github.com/Ayushhhh188/AI-Augmented_Library_Management_System/blob/3d82ad2f9ab882cfeb1922d8f55a45ffc0072d7e/static/Screenshot%202026-05-20%20003757.png)

### The platform enables employees to:
- Upload and manage enterprise documents
- Perform intelligent document searches
- Access digital library resources
- Interact with an AI-powered assistant capable of answering queries directly from uploaded documents
- Retrieve context-aware answers using semantic similarity search and local LLM inference

The system is designed to simulate a scalable enterprise-grade internal knowledge management platform suitable for industrial, mining, operational, environmental, and safety documentation workflows.

---

## Key Features

### Traditional Library Management Features

#### User Authentication
- Secure Google OAuth authentication
- Session-based login management
- Role-based access control
- Admin and employee-level authorization

#### Document Management
- Upload PDF, DOCX, DOC, and TXT files
- Bulk document uploads
- Document metadata storage
- File management system
- Uploaded document tracking

#### Search System
- Search documents by title
- Advanced metadata-based search
- Recently added document retrieval
- Semantic AI-assisted retrieval

#### Admin Controls
- User management
- Document monitoring
- Access restriction handling
- Administrative dashboard

---

### AI-Augmented RAG Architecture

The system integrates a fully local Retrieval-Augmented Generation (RAG) pipeline.

Unlike conventional chatbot integrations that rely on external APIs, this system performs:
- Local vector embedding generation
- Semantic similarity search
- Context retrieval
- Local LLM inference
- Grounded answer generation

#### This allows:
- Offline enterprise AI functionality
- No dependency on paid APIs
- Domain-specific document intelligence
- Privacy-preserving inference

---

## RAG Pipeline Architecture

### Step 1 — Document Upload
Uploaded documents are stored inside:
staic/uploads

Supported formats:
- PDF
- DOCX
- DOC
- TXT

### Step 2 — Document Parsing
Documents are processed using:
- `PyPDF2` for PDF extraction
- `python-docx` for DOCX extraction
- UTF-8 text parsing for TXT files

Text extraction pipeline:
Document → Text Extraction → Raw Content

### Step 3 — Intelligent Chunking
Large documents are split into semantically meaningful chunks using:
- `RecursiveCharacterTextSplitter`

Chunking strategy:
- `chunk_size = 700`
- `chunk_overlap = 120`

This improves:
- Retrieval precision
- Semantic locality
- Answer grounding
- Context preservation

### Step 4 — Embedding Generation
Each chunk is converted into dense vector embeddings using:
- `Sentence Transformers`

Embedding model:
- `all-MiniLM-L6-v2`

### Step 5 — Vector Database Storage
Embeddings are stored in:
- `ChromaDB`

Stored data includes:
- Embeddings
- Document chunks
- Metadata
- Source references

### Step 6 — Semantic Retrieval

When a user asks a question:
User Query → Query Embedding → Vector Similarity Search → Top Relevant Chunks Retrieved

The system retrieves semantically related document sections instead of performing simple keyword matching.
### Step 7 — Local LLM Inference

Retrieved chunks are passed into a locally running Small Language Model through:

    Ollama

Supported models:

    Phi-3

    Mistral

Inference architecture:
Flask → Ollama API → Local SLM → Grounded Response
Prompt Engineering

The system uses strict prompt engineering rules to reduce hallucinations.

The AI assistant:

    Answers strictly from retrieved context

    Avoids fabricated responses

    Rejects unsupported claims

    Handles greetings and conversational queries

    Maintains enterprise-style responses

### Project Architecture
Layer	Technology
Backend	Flask, Python
Database	MongoDB Atlas
Vector Database	ChromaDB
AI / NLP Stack	Sentence Transformers, LangChain Text Splitters, Ollama, Phi-3 / Mistral
Frontend	HTML, CSS, JavaScript
Authentication	Google OAuth

##Chatbot Workflow
User Question
      ↓
Flask Route
      ↓
RAG Pipeline
      ↓
Embedding Generation
      ↓
Vector Search
      ↓
Relevant Chunks Retrieved
      ↓
Prompt Construction
      ↓
Phi3 / Mistral
      ↓
Grounded AI Response

Installation
1. Clone Repository
bash

git clone <repository_url>
cd cc_library_system_rag

2. Create Virtual Environment
bash

python -m venv venv

Activate:

    Windows:
    bash

    venv\Scripts\activate

    Linux/Mac:
    bash

    source venv/bin/activate

3. Install Dependencies
bash

pip install -r requirements.txt

4. Ollama Setup

Install Ollama: https://ollama.com

Pull model:
bash: ollama pull phi3

or
bash: ollama pull mistral

Run model:
bash: ollama run phi3

5. Environment Variables

Create .env:
env

SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_uri
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

6. Run Application

Terminal 1 — Run Ollama:
bash: ollama run phi3

Terminal 2 — Run Flask app:
bash: python app.py

### Internship Statement

This project was developed as part of an internship initiative focused on exploring the integration of Artificial Intelligence, Retrieval-Augmented Generation (RAG), semantic search, and enterprise document management systems within industrial organizational workflows.
### License

This project is intended for educational, research, and demonstration purposes.

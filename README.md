# AI-Based Customer Experience Solution
### Designing an AI-Based Customer Experience Framework for Small Businesses Using Retrieval-Augmented Generation and Large Language Models

**Submitted by:** Laxman Singh (Enrollment No. O24MCA112069)
**Guide:** Mr. Vikas Kumar Atray
**Department:** Computer Applications, Chandigarh University
**Academic Session:** 2024–2026

This repository contains the working implementation that accompanies the
dissertation. It is a full-stack application consisting of a **React.js**
frontend and a **FastAPI** backend that together provide an AI-powered
customer support chatbot grounded in a business's own documents using
**Retrieval-Augmented Generation (RAG)**.

---

## 1. System Overview

| Layer            | Technology                                   |
|-------------------|-----------------------------------------------|
| Frontend          | React.js (Vite), React Router, Axios          |
| Backend           | FastAPI (Python 3.12)                         |
| Relational DB     | SQLite                                        |
| Vector Database   | ChromaDB                                      |
| Embedding Model   | Sentence Transformers (`all-MiniLM-L6-v2`)    |
| Large Language Model | Ollama (local, e.g. Llama 3) or OpenAI (cloud) |
| Authentication    | JWT session tokens + bcrypt password hashing  |

This matches Table 4.1 (Development Environment) of the dissertation.

---

## 2. Project Structure

```
AI-Customer-Support/
│
├── frontend/                 React.js customer & admin interface
│   ├── src/
│   │   ├── components/       Reusable UI components (nav bar, chat bubble)
│   │   ├── pages/             Login, Chat, Dashboard, Document Upload
│   │   ├── services/api.js   Axios API client
│   │   └── App.jsx
│   └── package.json
│
├── backend/                   FastAPI application
│   ├── api/                   Route definitions (auth, chat, documents, dashboard)
│   ├── models/                 Pydantic request/response schemas
│   ├── services/               Auth, document processing, semantic search, AI generation
│   ├── database/               SQLAlchemy models (SQLite)
│   ├── chatbot/                Conversation/session memory management
│   ├── rag/                    Retrieval-Augmented Generation pipeline
│   └── main.py                 Application entry point
│
├── documents/                  Sample business documents (FAQ, policies)
├── chromadb/                    Vector database storage (created automatically)
├── uploads/                     Uploaded document storage (created automatically)
└── README.md                    This file
```

---

## 3. Prerequisites

Install the following before setup:

1. **Python 3.12** (or 3.10+) — https://www.python.org/downloads/
2. **Node.js 18+** and npm — https://nodejs.org/
3. **Git** — https://git-scm.com/
4. **Ollama** (only if you want to run the LLM locally, recommended for the
   default configuration) — https://ollama.com/download

Operating system used for development and testing: **Ubuntu 22.04 LTS**
(the steps below also work on Windows and macOS with minor path differences,
noted where relevant).

---

## 4. Backend Setup

Open a terminal in the project's `backend/` folder.

### 4.1 Create and activate a virtual environment

```bash
cd backend
python3 -m venv venv

# Activate it:
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 4.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 4.3 Configure environment variables

```bash
cp .env.example .env         # Linux / macOS
copy .env.example .env       # Windows
```

Open `.env` and review the values. The defaults work for local development.
At minimum, confirm:

- `LLM_PROVIDER=ollama` (default, runs the model locally) **or**
  `LLM_PROVIDER=openai` (requires `OPENAI_API_KEY` to be set)
- `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` — the administrator
  account that is created automatically the first time the server starts

### 4.4 Set up the local LLM (Ollama) — skip if using OpenAI

```bash
# Install Ollama, then pull the model referenced in .env (default: llama3)
ollama pull llama3

# Start the Ollama service (usually runs automatically after install)
ollama serve
```

If you prefer OpenAI instead of a local model, set `LLM_PROVIDER=openai` and
`OPENAI_API_KEY=<your key>` in `.env` — no local model download is needed.

### 4.5 Run the backend server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- The API will be available at **http://localhost:8000**
- Interactive Swagger documentation is available at **http://localhost:8000/docs**
- On first startup, the SQLite database and default administrator account
  are created automatically (no manual migration step required).

### 4.6 Load the sample knowledge base (optional, recommended for a demo)

The `/documents` folder contains a sample FAQ/policy document. Once the
backend is running, log in as the administrator and upload it through the
**Documents** page in the frontend (Section 6 below), or upload it directly
via the Swagger UI at `/docs` using the `/upload` endpoint.

---

## 5. Frontend Setup

Open a **second terminal** in the project's `frontend/` folder (leave the
backend running in the first terminal).

```bash
cd frontend
npm install
cp .env.example .env      # Linux / macOS
copy .env.example .env    # Windows
npm run dev
```

The frontend will be available at **http://localhost:5173**

---

## 6. Using the Application

1. Open **http://localhost:5173** in a browser.
2. The **Chat** page is the default customer-facing view — try asking:
   *"What is your return policy?"* or *"Do you ship internationally?"*
   (these are answered from the sample document once it is uploaded).
3. Click **Admin Login** and sign in with the credentials from your `.env`
   file (default: `admin` / `Admin@12345`).
4. From the **Documents** page, upload PDF, DOCX, or TXT business documents.
   Each upload is automatically split into chunks, embedded, and stored in
   ChromaDB for retrieval.
5. The **Dashboard** page shows total documents, conversations, and recent
   uploads.

**Important:** change the default administrator password immediately after
first login using the `/change-password` endpoint (there is no dedicated
UI screen for this in the current build — call it from `/docs` or extend
the frontend as an enhancement).

---

## 7. API Reference

All endpoints are documented interactively at `http://localhost:8000/docs`.
Summary (matches Section 4.15.2 of the dissertation):

**Authentication**
| Method | Endpoint          | Purpose                        |
|--------|-------------------|---------------------------------|
| POST   | `/login`          | Administrator login            |
| POST   | `/logout`         | End user session                |
| POST   | `/change-password`| Update administrator password  |

**Chatbot**
| Method | Endpoint    | Purpose                        |
|--------|-------------|---------------------------------|
| POST   | `/chat`     | Submit customer query          |
| GET    | `/history`  | Retrieve conversation history  |
| GET    | `/session`  | Retrieve active chat session   |

**Documents**
| Method | Endpoint              | Purpose                    |
|--------|-----------------------|------------------------------|
| POST   | `/upload`             | Upload new document        |
| GET    | `/documents`          | List uploaded documents    |
| DELETE | `/documents/{id}`     | Delete a document          |

**Dashboard**
| Method | Endpoint      | Purpose                     |
|--------|---------------|-------------------------------|
| GET    | `/dashboard`  | Dashboard summary statistics |
| GET    | `/analytics`  | Chatbot usage statistics     |
| GET    | `/logs`       | Application activity logs    |

---

## 8. How the RAG Pipeline Works (Chapter 4 reference)

1. Customer submits a question through `/chat` (Figure 4.8).
2. The question is embedded using Sentence Transformers.
3. ChromaDB is searched for the most semantically similar document chunks
   (cosine similarity) — Figure 4.6.
4. If relevant chunks are found above the similarity threshold, they are
   combined with the question into a single prompt.
5. The prompt is sent to the configured LLM (Ollama or OpenAI) — Figure 4.7.
6. The response is post-processed, stored in the Chat History table, and
   returned to the frontend.
7. If no relevant chunks are found, the chatbot responds honestly that it
   does not have that information, instead of guessing (Section 4.14.7).

---

## 9. Troubleshooting

| Problem                                        | Likely cause / fix                                                        |
|-------------------------------------------------|-----------------------------------------------------------------------------|
| `Connection refused` from frontend to backend  | Backend not running, or `VITE_API_BASE_URL` in frontend `.env` is wrong   |
| Chatbot replies "having trouble generating..." | Ollama isn't running (`ollama serve`) or model not pulled (`ollama pull llama3`) |
| Login always fails                             | Check `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` in backend `.env`, delete `database/app.db` to reset if changed after first run |
| Upload fails immediately                        | Only `.pdf`, `.docx`, `.txt` are supported; file must be under 20 MB       |
| `ModuleNotFoundError` on backend start          | Virtual environment not activated, or `pip install -r requirements.txt` not run |
| CORS error in browser console                   | `FRONTEND_ORIGIN` in backend `.env` must match the URL the frontend is served from |

---

## 10. Notes for Evaluators / Examiners

- This implementation directly mirrors the architecture, modules, database
  schema (Tables 3.1–3.4), and API design (Section 4.15) described in the
  dissertation.
- The default configuration uses a **local** LLM via Ollama so the system
  can be demonstrated fully offline with no API costs — matching the
  dissertation's emphasis on data privacy for small businesses (Section 4.19).
- Switching to OpenAI only requires changing `LLM_PROVIDER` and supplying an
  API key — no code changes are required, demonstrating the modular AI
  integration described in Section 3.4 (Technology Stack).

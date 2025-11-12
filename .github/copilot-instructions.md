# Copilot Instructions for RAG Chatbot Project

## Project Overview

- **Frontend:** React.js + Tailwind CSS for a responsive chat UI.
- **Backend:** FastAPI for API endpoints, web scraping, chunking, retrieval, and answer generation.
- **Goal:** User asks a question; backend scrapes a website, chunks and stores content, retrieves relevant context, and generates an answer using an LLM.

## Key Developer Workflows

- **Start backend:** `uvicorn app.main:app --reload` (from `/backend`)
- **Start frontend:** `npm start` or `yarn start` (from `/frontend`)
- **Install backend deps:** `pip install -r requirements.txt`
- **Install frontend deps:** `npm install` or `yarn`
- **Test backend:** `pytest` (if tests exist)
- **API docs:** FastAPI interactive docs at `/docs`

## Backend Structure & Patterns

- **Scraping:** Use a web loader (BeautifulSoup, Playwright, or Scrapy) in `app/scraper.py`.
- **Chunking:** Split text into chunks in `app/chunker.py`.
- **Retrieval:** Store and retrieve chunks (consider FAISS/ChromaDB) in `app/retriever.py`.
- **LLM Integration:** Generate answers in `app/llm.py` (use OpenAI/HuggingFace APIs).
- **API Endpoints:**
  - `POST /api/scrape` — Scrape and chunk website content.
  - `POST /api/chat` — Retrieve context and generate answer.

## Frontend Structure & Patterns

- **Chat UI:** `src/components/Chatbot.jsx` for chat interface.
- **API Calls:** Use `src/api.js` to communicate with backend endpoints.
- **Styling:** Use Tailwind utility classes; avoid custom CSS.

## Project Conventions

- All scraping, chunking, and retrieval logic is backend-only.
- Use REST endpoints for all chat and scraping actions.
- Store and retrieve context in chunks for efficient retrieval.
- Use Tailwind for all styling.

## Integration Points

- Frontend calls backend via `/api/chat` and `/api/scrape`.
- Backend may call external LLM APIs for answer generation.
- Scraping logic should handle dynamic sites if needed.

## Example API Flow

1. `POST /api/scrape` with `{ url }` — Scrapes and chunks content.
2. `POST /api/chat` with `{ question }` — Retrieves relevant chunks, generates answer.

## Key Files/Directories

- Backend: `app/main.py`, `app/scraper.py`, `app/chunker.py`, `app/retriever.py`, `app/llm.py`
- Frontend: `src/components/Chatbot.jsx`, `src/App.jsx`, `tailwind.config.js`

---

Update this file as the project evolves. For unclear or missing sections, ask for clarification or examples from the team.

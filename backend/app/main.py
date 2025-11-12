from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.scraper import scrape_website
from app.chunker import chunk_text
from app.retriever import store_chunks, retrieve_relevant_chunks
from app.llm import generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scrape")
async def scrape_endpoint(request: Request):
    data = await request.json()
    url = data.get("url")
    text = scrape_website(url)
    chunks = chunk_text(text)
    store_chunks(chunks)
    return {"message": "Scraping and chunking complete", "chunks": len(chunks)}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    question = data.get("question")
    context = retrieve_relevant_chunks(question)
    answer = generate_answer(question, context)
    return {"answer": answer, "context": context}

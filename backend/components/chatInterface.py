import logging 
import os
import chromadb 
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatInterface")

chroma_client = chromadb.Client(Settings())
collection = chroma_client.create_collection("rag_demo")

def load_and_store_webpage(url,collection,chunk_size=1000,chunk_overlap = 200):
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
	)
    chunks = text_splitter.split_documents(docs)
    for i , chunk in enumerate(chunks):
        collection.add(
            documents=[chunk.page_content],
            ids=[f"web-{i}"]
		)
        
if collection.count() == 0:
    load_and_store_webpage(
        "https://python.langchain.com/docs/tutorials/rag/",
        collection,
        chunk_size=1000,
        chunk_overlap=200
	)
    
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("No API_KEY found")
    
def gemini_generate(query,context,api_key):
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = f"context:\n{context}\n\nQuestion:{query}\nAnswer:"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini model error: {e}")
        raise
    
def get_rag_response(query: str) -> str:
    query_embedding = embedding_fn([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    retrieved_text = [doc for doc in results["documents"][0]]
    logger.info(f"Retrieved docs:{retrieved_text}")
    context = "\n".join(retrieved_text)
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not set.")
    return gemini_generate(query, context, GEMINI_API_KEY)
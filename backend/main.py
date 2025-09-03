import logging 
from fastapi import FastAPI , Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from components.chatInterface import get_rag_response
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message" : "RAG API is running"}

@app.post("/rag")
async def rag_endpoint(request : Request):
    try:
        data = await request.json()
        query = data.get("query","")
        if not query:
            raise HTTPException(status_code=400, detail = "Query is required.")
        logger.info(f"{query}")
        try:
            rag_result = get_rag_response(query)
        except Exception as e:
            logger.error(f"Error:{e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return {"Result":rag_result}
    except Exception as e:
        logger.error(f"Error in /rag: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

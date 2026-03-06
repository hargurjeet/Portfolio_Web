# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
import os
import sys
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your core modules
from core.vector_store import load_vector_store
from core.rag_chain import ask
from config import INDEX_PATH

app = FastAPI(title="Hargurjeet's Portfolio RAG API")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Streamlit app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    chat_history: list = []

# Load vector store at startup
logger.info("🔵 Loading vector store...")
try:
    vector_store = load_vector_store(INDEX_PATH)
    logger.info(f"✅ Vector store loaded successfully from {INDEX_PATH}")
    logger.info(f"📊 Vector store type: {type(vector_store)}")
except Exception as e:
    logger.error(f"❌ Failed to load vector store: {e}")
    vector_store = None

@app.get("/")
async def root():
    return {
        "message": "Hargurjeet's Portfolio RAG API",
        "status": "running",
        "vector_store_loaded": vector_store is not None
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy" if vector_store else "degraded",
        "vector_store_loaded": vector_store is not None
    }

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    # Check if vector store is loaded
    if vector_store is None:
        logger.error("❌ Vector store not loaded")
        raise HTTPException(status_code=500, detail="Vector store not loaded")
    
    logger.info(f"📝 Received question: {request.question}")
    logger.info(f"📝 Chat history length: {len(request.chat_history)}")
    
    async def generate():
        try:
            # Call the RAG chain
            logger.info("🔵 Calling ask() function...")
            result = ask(vector_store, request.question, request.chat_history)
            
            # Extract answer and sources
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])
            
            logger.info(f"✅ Answer received, length: {len(answer)} characters")
            logger.info(f"📄 Sources count: {len(sources)}")
            
            if not answer:
                logger.warning("⚠️ Empty answer received")
                answer = "I couldn't find an answer to your question."
            
            # Format sources for frontend
            sources_data = []
            for doc in sources:
                sources_data.append({
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "?")
                })
            
            # Send sources first (if any)
            if sources_data:
                sources_json = json.dumps({"sources": sources_data})
                yield f"data: {sources_json}\n\n"
                logger.info(f"✅ Sent sources data")
            
            # Stream the answer token by token
            # This creates a nice typing effect in the UI
            for i, char in enumerate(answer):
                token_json = json.dumps({"token": char})
                yield f"data: {token_json}\n\n"
                
                # Log progress occasionally
                if i % 20 == 0:
                    logger.info(f"📤 Streamed {i} characters")
                
                # Small delay for visual effect (remove if you want instant)
                await asyncio.sleep(0.01)
            
            # Send completion signal
            yield "data: [DONE]\n\n"
            logger.info("✅ Streaming completed")
            
        except Exception as e:
            logger.error(f"❌ Error in generate: {str(e)}")
            import traceback
            traceback.print_exc()
            error_json = json.dumps({"error": str(e)})
            yield f"data: {error_json}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
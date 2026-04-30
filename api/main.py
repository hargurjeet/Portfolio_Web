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
from core.rag_chain import retrieve_docs, build_prompt, build_llm
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
            loop = asyncio.get_running_loop()

            # Fast sync retrieval — FAISS lookup takes milliseconds
            docs = retrieve_docs(vector_store, request.question)
            context = "\n\n".join(doc.page_content for doc in docs)
            messages = build_prompt(request.question, context, request.chat_history)
            logger.info(f"📄 Retrieved {len(docs)} docs, built prompt")

            # Send sources SSE immediately before LLM starts
            sources_data = [
                {"source": d.metadata.get("source", "Unknown"), "page": d.metadata.get("page", "?")}
                for d in docs
            ]
            if sources_data:
                yield f"data: {json.dumps({'sources': sources_data})}\n\n"

            # Bridge sync token generator → async SSE via queue
            # stream_tokens() is a sync generator running in a thread executor;
            # it pushes each token into the asyncio queue via call_soon_threadsafe.
            queue: asyncio.Queue = asyncio.Queue()
            _SENTINEL = object()

            def _run_stream():
                try:
                    llm = build_llm()
                    for token in llm.stream_tokens(messages):
                        loop.call_soon_threadsafe(queue.put_nowait, token)
                except Exception as exc:
                    logger.error(f"❌ stream_tokens error: {exc}")
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, _SENTINEL)

            loop.run_in_executor(None, _run_stream)

            token_count = 0
            while True:
                item = await queue.get()
                if item is _SENTINEL:
                    break
                yield f"data: {json.dumps({'token': item})}\n\n"
                token_count += 1

            logger.info(f"✅ Streamed {token_count} tokens")
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"❌ Error in generate: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
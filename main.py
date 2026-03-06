# import logging
# import warnings
# import hashlib

# logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
# warnings.filterwarnings("ignore")

# import os
# from config import DOCS_PATH, INDEX_PATH
# from core.loader import load_documents
# from core.splitter import split_documents
# from core.vector_store import create_vector_store, load_vector_store
# from core.rag_chain import ask

# def get_docs_hash(docs_path):
#     """Hash all filenames + modified times to detect changes."""
#     files = sorted(
#         (f, os.path.getmtime(os.path.join(docs_path, f)))
#         for f in os.listdir(docs_path)
#     )
#     return hashlib.md5(str(files).encode()).hexdigest()

# HASH_FILE = os.path.join(INDEX_PATH, "docs_hash.txt")

# def index_is_stale():
#     if not os.path.exists(INDEX_PATH) or not os.path.exists(HASH_FILE):
#         return True
#     with open(HASH_FILE) as f:
#         old_hash = f.read().strip()
#     return old_hash != get_docs_hash(DOCS_PATH)

# def save_docs_hash():
#     os.makedirs(INDEX_PATH, exist_ok=True)
#     with open(HASH_FILE, "w") as f:
#         f.write(get_docs_hash(DOCS_PATH))

# def main():
#     if index_is_stale():
#         print(f"Docs changed or no index found — rebuilding from: {DOCS_PATH}")
#         docs = load_documents(DOCS_PATH)
#         chunks = split_documents(docs)
#         vector_store = create_vector_store(chunks, INDEX_PATH)
#     else:
#         vector_store = load_vector_store(INDEX_PATH)

#     print("\n🤖 RAG Pipeline ready! Type 'exit' to quit.\n")
#     chat_history = []
#     while True:
#         question = input("Ask a question: ").strip()
#         if question.lower() in ("exit", "quit"):
#             break
#         if question:
#             result = ask(vector_store, question, chat_history)
#             # Update history for next turn
#             chat_history.append([question, result["answer"]])


# if __name__ == "__main__":
#     main()

# In your FastAPI file (e.g., api/main.py)
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vector_store import load_vector_store
from core.rag_chain import ask
from config import INDEX_PATH

app = FastAPI()

# Load vector store once at startup
print("🔵 Loading vector store...")
try:
    vector_store = load_vector_store(INDEX_PATH)
    print(f"🔵 Vector store loaded successfully: {type(vector_store)}")
except Exception as e:
    print(f"🔴 Failed to load vector store: {e}")
    vector_store = None

@app.post("/api/v1/chat")
async def chat(request: dict):
    if vector_store is None:
        return {"error": "Vector store not loaded"}
    
    question = request.get("question", "")
    chat_history = request.get("chat_history", [])
    
    print(f"\n🔵 API received question: {question}")
    print(f"🔵 Chat history length: {len(chat_history)}")
    
    async def generate():
        try:
            print("🔵 Calling ask() function...")
            result = ask(vector_store, question, chat_history)
            
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])
            
            print(f"🔵 Answer received: {answer[:100]}...")
            print(f"🔵 Answer length: {len(answer)}")
            
            if not answer:
                print("🔴 Empty answer received!")
                answer = "I couldn't find an answer to your question."
            
            # Format sources
            sources_data = []
            for doc in sources:
                sources_data.append({
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "?")
                })
            
            # Send sources
            if sources_data:
                yield f"data: {json.dumps({'sources': sources_data})}\n\n"
                print("🔵 Sources sent")
            
            # Send answer character by character
            for i, char in enumerate(answer):
                yield f"data: {json.dumps({'token': char})}\n\n"
                if i % 10 == 0:  # Log every 10th character
                    print(f"🔵 Sent char {i}: {char}")
                await asyncio.sleep(0.01)
            
            # Send completion
            yield "data: [DONE]\n\n"
            print("🔵 Streaming completed")
            
        except Exception as e:
            print(f"🔴 Error in generate: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "ok", "vector_store": vector_store is not None}
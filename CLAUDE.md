# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build/rebuild the FAISS vector index from the knowledge base PDF
python3.10 build_index.py

# Run the FastAPI backend (port 8000)
python3.10 -m uvicorn api.main:app --reload --port 8000

# Run the Streamlit frontend (port 8501)
python3.10 -m streamlit run ui/streamlit_app.py --server.port 8501

# Run both services together (production-style)
bash start.sh

# CLI chatbot for quick RAG testing without the UI
python3.10 main.py

# Health check
curl http://localhost:8000/health

# Test the chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is his GenAI experience?", "chat_history": []}'

# Deploy to fly.io (must run from this directory)
flyctl deploy --app hargurjeet-portfolio
```

## Environment Variables

Copy `.env.example` or create `.env` in the project root:
```
FIREWORKS_API_KEY=...   # Required for LLM responses
OPENAI_API_KEY=...      # Legacy; not used by the active LLM path
```

On fly.io, secrets are set via `flyctl secrets set FIREWORKS_API_KEY=...`.

## Architecture

This is a **RAG-powered portfolio chatbot** with two processes running in a single container:

```
Browser → Streamlit (port 8501) → FastAPI (port 8000) → Fireworks AI API
                                         ↓
                                    FAISS index (local disk)
                                         ↓
                              HuggingFace embedding model
                              (all-mpnet-base-v2, 768-dim)
```

### Key architectural facts

**Two FastAPI entry points exist — only `api/main.py` is active:**
- `api/main.py` — the real entry point used by `start.sh` and fly.io. Defines `/api/v1/chat` directly on the app (not via router), loads the vector store at module startup, simulates streaming by sending characters one-by-one with a 10ms delay.
- `api/routes/chat.py` — a secondary router that is **not mounted** in `api/main.py`. It uses `AsyncIteratorCallbackHandler` for true token-level streaming from `FireworksLLM`. It was the original HuggingFace Spaces version.

**LLM**: Custom `FireworksLLM` class (`core/fireworks_llm.py`) wraps the Fireworks AI REST API directly. Model is `accounts/fireworks/models/qwen3-8b`. The class strips `<think>...</think>` blocks (chain-of-thought) from responses before returning them.

**Vector store**: FAISS index stored at `faiss_index/` (excluded from git, included in Docker). The index is built from `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf` using `build_index.py`. If `faiss_index/` is missing, run `build_index.py` before starting the API.

**Embedding model**: `sentence-transformers/all-mpnet-base-v2` loaded via `langchain-huggingface`. The Dockerfile pre-downloads this model into the image layer (`RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"`) to avoid slow cold starts on fly.io.

**Startup order**: `start.sh` starts FastAPI and Streamlit in parallel. FastAPI takes ~30–60s to load the FAISS index; Streamlit comes up in seconds. The Streamlit UI handles `ConnectionRefusedError` gracefully while FastAPI is still loading.

**All RAG config** (`CHUNK_SIZE`, `TOP_K`, model names, paths) is centralised in `config.py`.

## fly.io Deployment

- App name: `hargurjeet-portfolio`
- Region: `sin` (Singapore)
- Config: `fly.toml` in this directory — deploy is always run from the `Portfolio_Web/` root
- Internal port `8501` (Streamlit) is exposed publicly; FastAPI on `8000` is internal-only
- The `FIREWORKS_API_KEY` secret must be set on the fly.io app, not in `.env`

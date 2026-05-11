# Portfolio Web — Claude Context

## What This Project Does

A RAG-powered portfolio chatbot. Users visit the Streamlit UI, ask questions about Hargurjeet, and receive streamed answers drawn from a FAISS vector index built from a PDF knowledge base. The UI also has tabs for Experience, Resume download, Blogs, and Projects.

**Live at**: https://huggingface.co/spaces/Hargurjeet/portfolio-chatbot (HuggingFace Spaces, Docker SDK)

## Stack

- **Backend**: FastAPI (port 8000, internal-only) — SSE streaming endpoint
- **Frontend**: Streamlit (port 8501, public) — custom CSS, Comic Sans MS, 5-tab layout
- **LLM**: Fireworks AI — `accounts/fireworks/models/qwen3-8b` via custom `FireworksLLM` class
- **Embeddings**: `sentence-transformers/all-mpnet-base-v2` (768-dim, CPU, normalised)
- **Vector store**: FAISS index stored at `faiss_index/` (tracked via git LFS)
- **Deployment**: Single Docker container on HuggingFace Spaces (Docker SDK, port 8501)
- **Package manager**: `pip` / `requirements.txt` (also has `pyproject.toml` + `uv.lock` for uv)
- **CI/CD**: GitHub Actions auto-syncs to HuggingFace Spaces on every push to `main`
- **Remotes**: `github` → GitHub (primary), `space` → HuggingFace Spaces (legacy, superseded by Actions)

## Key Files

| File | Role |
|------|------|
| `api/main.py` | **Active** FastAPI entry point — `/api/v1/chat`, `/health`, `/` |
| `core/fireworks_llm.py` | Custom LangChain LLM wrapping Fireworks REST API directly; handles think-block stripping |
| `core/rag_chain.py` | `build_prompt()`, `build_llm()`, `ask()`, `ask_stream()` |
| `core/vector_store.py` | FAISS load/save with HuggingFace embeddings |
| `core/loader.py` | PDF/text loader via `PyPDFLoader` |
| `core/splitter.py` | `RecursiveCharacterTextSplitter` (chunk=200, overlap=50) |
| `config.py` | All tuneable constants — chunk size, TOP_K, model IDs, paths |
| `ui/streamlit_app.py` | Full Streamlit UI — topbar, 5 tabs, SSE chat, experience/blogs/projects data |
| `build_index.py` | One-shot script: load PDF → chunk → embed → save FAISS index |
| `start.sh` | Launches FastAPI + Streamlit in parallel; `wait -n; wait` keeps container alive |
| `Dockerfile` | Python 3.10-slim; pre-downloads embedding model into image layer |
| `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf` | Source document for FAISS index |
| `data/Hargurjeet _Agenti_AI_Specialist_2026.pdf` | Resume PDF served for download in UI |
| `data/my_avatar.png` | Avatar shown in the topbar |
| `faiss_index/` | Pre-built FAISS index (`index.faiss` + `index.pkl`) — git LFS, included in Docker |
| `.github/workflows/sync-to-hf.yml` | GitHub Action — syncs to HF Spaces on every push to `main` via `huggingface_hub.upload_folder()` |

### Dead code — do not touch or treat as active

| File | Status |
|------|--------|
| `api/routes/chat.py` | **Not mounted** — original HF Spaces version using `AsyncIteratorCallbackHandler`. Defined as a router but never added to `api/main.py`. |
| `main.py` (root) | **Mostly commented out** — was the original CLI chatbot. Lower half contains a duplicate FastAPI stub used for debugging. Not run in production. |

## Data Flow

```
POST /api/v1/chat  { question, chat_history }
  → FAISS similarity search (TOP_K=4 docs)
  → build_prompt() → system + context + history + question (messages list)
  → thread executor: FireworksLLM.stream_tokens() → sync SSE generator
     → stateful think-block stripper (buffering → in_think → yielding)
  → asyncio.Queue bridges sync generator → async SSE
  → SSE frames: sources first, then tokens, then [DONE]

Streamlit _sse_token_generator()
  → consumes SSE, yields tokens to st.write_stream()
  → pending_sources[] populated from "sources" frame
  → on [DONE]: rerun() to finalise state
```

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build/rebuild the FAISS vector index from the knowledge base PDF
python build_index.py

# Run FastAPI backend (port 8000)
uvicorn api.main:app --reload --port 8000

# Run Streamlit frontend (port 8501)
streamlit run ui/streamlit_app.py --server.port 8501

# Run both together (production-style)
bash start.sh

# Health check
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is his GenAI experience?", "chat_history": []}'

# Deploy — just push to GitHub; Actions auto-syncs to HF Spaces
git push github main
```

## Environment Variables

Create `.env` in the project root (git-ignored):
```
FIREWORKS_API_KEY=fw_...
```

On HuggingFace Spaces, set via: Settings → Variables and secrets → New secret

Stale/unused vars still in `config.py` (safe to ignore):
- `OPENAI_API_KEY` — not used
- `LLM_MODEL = "gpt-5-nano"` — not used

## Configuration (config.py)

| Constant | Value | Notes |
|----------|-------|-------|
| `DOCS_PATH` | `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf` | Source for FAISS index |
| `INDEX_PATH` | `faiss_index` | FAISS index directory |
| `EMBEDDING_MODEL` | `all-mpnet-base-v2` | HuggingFace sentence-transformer |
| `CHUNK_SIZE` | 200 | Characters per chunk |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `TOP_K` | 4 | Documents retrieved per query |
| `FIREWORKS_MODEL` | `accounts/fireworks/models/qwen3-8b` | Active LLM |
| `FIREWORKS_TEMPERATURE` | 0.6 | |
| `FIREWORKS_MAX_TOKENS` | 512 | |

## Think-Block Stripping

`FireworksLLM.stream_tokens()` implements a 3-state machine to strip `<think>...</think>` blocks from Qwen3's chain-of-thought output before streaming tokens to the client:

- **`buffering`**: accumulate until `<think>` prefix detected or buffer ≥ 50 chars
- **`in_think`**: discard tokens until `</think>` found, then switch to `yielding`
- **`yielding`**: pass tokens directly to caller

Controlled by `hide_think_blocks=True` on the LLM instance.

## HuggingFace Spaces Deployment Details

- Space: `Hargurjeet/portfolio-chatbot`
- SDK: Docker (`sdk: docker` in README frontmatter)
- Exposed port: `8501` (Streamlit) — only this port is accessible publicly; FastAPI on `8000` is internal-only
- **Deploy**: push to `github main` → GitHub Actions runs `.github/workflows/sync-to-hf.yml` → uploads to HF Spaces automatically (tested, working)
- GitHub secret required: `HF_TOKEN` (set in repo Settings → Secrets → Actions)
- HF Spaces secret required: `FIREWORKS_API_KEY` (set in Space Settings → Variables and secrets)
- HF Spaces does not guarantee always-on; Streamlit's `/health` polling loop handles cold-start gracefully

## Known Issues / Security Notes

- **HF token in git remote URL**: The `space` remote URL contains a plaintext HF token. Rotate it at huggingface.co/settings/tokens if still active. Fix with: `git remote set-url space https://huggingface.co/spaces/Hargurjeet/portfolio-chatbot`
- **Wide-open CORS**: `allow_origins=["*"]` — acceptable for a public portfolio, but worth tightening if the API is ever used for anything sensitive
- **FAISS index in git LFS**: `faiss_index/index.faiss` and `faiss_index/index.pkl` are tracked via LFS. Rebuild with `build_index.py` if the knowledge base PDF changes
- **No tests**: `tests/` directory exists but is empty

## Docs

- `docs/architecture.md` — full system design and data flow
- `docs/api.md` — API endpoint reference
- `docs/setup.md` — local and Docker setup guide
- `docs/deployment.md` — HuggingFace Spaces deployment details and operations
- `docs/data-models.md` — request/response schemas and config reference

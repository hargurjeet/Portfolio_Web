# Architecture

## System Overview

A RAG-powered portfolio chatbot running two processes inside a single Docker container on HuggingFace Spaces.

```
Internet
    │
    ▼ port 8501 (public)
┌─────────────────────────────────────────┐
│            Docker Container              │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │    Streamlit UI (port 8501)     │    │
│  │    ui/streamlit_app.py          │    │
│  └──────────────┬──────────────────┘    │
│                 │ HTTP (localhost)       │
│                 ▼                        │
│  ┌─────────────────────────────────┐    │
│  │    FastAPI Backend (port 8000)  │    │
│  │    api/main.py                  │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│         ┌───────┴───────┐               │
│         ▼               ▼               │
│  ┌────────────┐  ┌────────────────┐    │
│  │  FAISS     │  │  Fireworks AI  │    │
│  │  index     │  │  (external)    │    │
│  │  (local)   │  │  qwen3-8b      │    │
│  └────────────┘  └────────────────┘    │
└─────────────────────────────────────────┘
```

## Request / Response Flow

### Chat Request (SSE Streaming)

```
User types question in Streamlit
    │
    ▼
st.session_state.awaiting_response = True
st.rerun()
    │
    ▼
_sse_token_generator() (Streamlit coroutine)
    │  POST /api/v1/chat { question, chat_history }
    ▼
FastAPI /api/v1/chat
    │
    ├── retriever.invoke(question)          ← FAISS similarity search, TOP_K=4
    │
    ├── build_prompt(question, context,     ← system prompt + RAG context +
    │       chat_history)                      prior turns + current question
    │
    ├── yield SSE "sources" frame           ← sent immediately before LLM starts
    │
    ├── loop.run_in_executor(               ← sync LLM in thread pool
    │       None, _run_stream)
    │       │
    │       └── FireworksLLM.stream_tokens()
    │               │  POST Fireworks REST API (SSE)
    │               │
    │               └── think-block stripper
    │                   (buffering → in_think → yielding)
    │
    ├── asyncio.Queue bridges sync → async
    │
    └── yield SSE "token" frames → yield "[DONE]"
    │
    ▼
Streamlit _sse_token_generator() yields tokens
    │
    ▼
st.write_stream() renders progressively
    │
    ▼
st.session_state.awaiting_response = False
st.rerun()  ← finalises message in session state
```

### Index Build Flow (one-time, offline)

```
build_index.py
    │
    ├── load_documents(DOCS_PATH)           ← PyPDFLoader
    │
    ├── split_documents(docs)               ← RecursiveCharacterTextSplitter
    │   chunk_size=200, overlap=50          separators=["\n\n","\n","."," "]
    │
    ├── HuggingFaceEmbeddings               ← all-mpnet-base-v2, 768-dim
    │   model_name="all-mpnet-base-v2"
    │
    └── FAISS.from_documents(chunks, emb)
        FAISS.save_local("faiss_index")
```

## Module Map

```
Portfolio_Web/
├── api/
│   ├── main.py             ← ACTIVE FastAPI app (entry point)
│   ├── schemas.py          ← Pydantic models for the router (unused by main.py)
│   └── routes/
│       └── chat.py         ← INACTIVE router (HF Spaces legacy, not mounted)
├── core/
│   ├── fireworks_llm.py    ← Custom LangChain LLM; stream_tokens() + think stripper
│   ├── rag_chain.py        ← build_prompt(), build_llm(), ask(), ask_stream()
│   ├── vector_store.py     ← FAISS load/save with HuggingFace embeddings
│   ├── loader.py           ← PDF/text document loader
│   └── splitter.py         ← Text chunking
├── ui/
│   └── streamlit_app.py    ← Full UI: topbar, 5 tabs, SSE streaming chat
├── data/
│   ├── Hargurjeet_Singh_Ganger_KnowledgeBase.pdf   ← RAG source document
│   ├── Hargurjeet_Lead_GenAI_Specialist.pdf         ← Resume (for download tab)
│   └── my_avatar.png                                ← Topbar avatar
├── faiss_index/
│   ├── index.faiss         ← Pre-built FAISS index (git LFS)
│   └── index.pkl           ← FAISS metadata (git LFS)
├── config.py               ← All tuneable constants
├── build_index.py          ← One-shot index builder
├── start.sh                ← Launches both processes in parallel
└── Dockerfile              ← Python 3.10-slim; pre-downloads embedding model
```

## Key Design Decisions

### Sync-in-thread-executor pattern
`FireworksLLM.stream_tokens()` is a synchronous generator (uses `requests` with `stream=True`). FastAPI's async endpoint bridges it to SSE via an `asyncio.Queue` and `loop.run_in_executor()`. This avoids blocking the event loop while allowing real token-level streaming.

### Sources sent before tokens
The SSE endpoint sends the `sources` frame immediately after FAISS retrieval — before the LLM starts streaming. The Streamlit client buffers sources in `pending_sources[]` and attaches them to the message after streaming completes.

### Think-block stripping
Qwen3 emits `<think>...</think>` chain-of-thought blocks before the actual answer. The 3-state machine in `stream_tokens()` detects and discards these without buffering the entire response — important for latency.

### Pre-built FAISS index
The index is built once and committed to git LFS. The Docker image includes it via `COPY . .`. This avoids a slow cold-start rebuild on every deploy. When the knowledge base PDF changes, run `python build_index.py` locally and commit the updated index files.

### Embedding model pre-downloaded
The Dockerfile runs `SentenceTransformer('all-mpnet-base-v2')` during build, caching the model weights into the image layer. This avoids a ~400 MB download on every cold start.

### Single container, two ports
FastAPI (8000) and Streamlit (8501) run in the same container managed by `start.sh`. HuggingFace Spaces only exposes port 8501 publicly (set via `app_port: 8501` in README frontmatter). FastAPI is reachable from Streamlit via `http://localhost:8000` internally.

## Startup Order

1. `start.sh` launches both processes in parallel with `&`
2. FastAPI starts but takes 30–60s to load the FAISS index and embedding model
3. Streamlit comes up in seconds and immediately serves the UI
4. Streamlit's `_backend_ready()` polls `localhost:8000/health` every second
5. While backend is not ready, Streamlit shows a warming-up banner and calls `st.rerun()`
6. Once `/health` returns 200, the chat interface becomes interactive

## UI Structure

```
Topbar (sticky)
├── Row 1: avatar · name/title · stats chips · social links
└── Row 2: skill tags (horizontal scroll)

Tabs
├── 💬 Chat
│   ├── Profile column (left): "What I Solve" + "Open To" cards
│   └── Chat column (right): scrollable message history + suggestion buttons + input
├── 🧭 Experience: career timeline (BT, Shell, TCS) + education
├── 📄 Resume: download button + inline PDF viewer
├── ✍️ Blogs: featured post + 26 blog links (Medium + LinkedIn)
└── 🚀 Projects: 4 project cards with banner images + live/github links
```

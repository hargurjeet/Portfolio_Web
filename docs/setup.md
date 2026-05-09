# Setup Guide

## Prerequisites

- Python 3.10 (specified in `.python-version`)
- A Fireworks AI API key (`FIREWORKS_API_KEY`)
- Docker (for container testing)

## Local Development

### 1. Install dependencies

```bash
# With pip
pip install -r requirements.txt

# Or with uv (lockfile is present)
uv sync
```

### 2. Create `.env`

```bash
echo "FIREWORKS_API_KEY=fw_your_key_here" > .env
```

The `.env` file is git-ignored. Never commit it.

### 3. Verify the FAISS index exists

```bash
ls faiss_index/
# Should show: index.faiss  index.pkl  .gitkeep
```

If the index files are missing (e.g., after a fresh git clone without LFS):
```bash
git lfs pull
```

If you need to rebuild from scratch:
```bash
python build_index.py
```

This reads `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf`, chunks it, embeds it with `all-mpnet-base-v2`, and writes `faiss_index/index.faiss` + `faiss_index/index.pkl`. Takes ~1–2 minutes on CPU.

### 4. Start the backend

```bash
uvicorn api.main:app --reload --port 8000
```

Wait for the log line:
```
✅ Vector store loaded successfully from faiss_index
✅ Retriever and LLM initialised
```

FastAPI takes 30–60 seconds to load the embedding model and FAISS index on first run.

### 5. Start the frontend (separate terminal)

```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

Open http://localhost:8501 in a browser.

### 6. Run both together

```bash
bash start.sh
```

Starts both processes in parallel. `wait -n; wait` keeps the shell alive until either process exits.

## Running with Docker

```bash
# Build image
docker build -t portfolio-web .

# Run container
docker run -p 8501:8501 -e FIREWORKS_API_KEY=fw_your_key_here portfolio-web
```

Open http://localhost:8501.

The Dockerfile pre-downloads the `all-mpnet-base-v2` model (~400 MB) into the image during build so cold starts don't need to fetch it.

The `faiss_index/` directory is included in the image via `COPY . .` — so the index must be present in the working directory before building.

### docker-compose

```bash
docker-compose up --build
```

`docker-compose.yml` is present in the project root if you prefer compose.

## Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Chat (streaming)
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is his GenAI experience?", "chat_history": []}'
```

## Rebuilding the Index

Run this any time `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf` changes:

```bash
python build_index.py
```

Then commit the updated `faiss_index/index.faiss` and `faiss_index/index.pkl` (they are tracked via git LFS).

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `FIREWORKS_API_KEY` | Yes | Fireworks AI API key for LLM inference |
| `OPENAI_API_KEY` | No | Legacy — not used by any active code path |
| `API_URL` | No | Override Streamlit's API URL (default: `http://localhost:8000/api/v1/chat`) |

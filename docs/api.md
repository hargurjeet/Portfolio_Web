# API Reference

FastAPI backend running on port 8000 (internal — not publicly exposed on HuggingFace Spaces).

Entry point: `api/main.py`

## Endpoints

### GET /

Health/info root.

**Response**
```json
{
  "message": "Hargurjeet's Portfolio RAG API",
  "status": "running",
  "vector_store_loaded": true
}
```

---

### GET /health

Used by Streamlit's cold-start polling loop.

**Response — healthy**
```json
{
  "status": "healthy",
  "vector_store_loaded": true,
  "llm_ready": true
}
```

**Response — degraded** (FAISS failed to load)
```json
{
  "status": "degraded",
  "vector_store_loaded": false,
  "llm_ready": false
}
```

---

### POST /api/v1/chat

Main chat endpoint. Returns a Server-Sent Events (SSE) stream.

**Request body**
```json
{
  "question": "What is his GenAI experience?",
  "chat_history": [
    ["previous user message", "previous assistant reply"]
  ]
}
```

- `question` — string, required
- `chat_history` — list of `[human, ai]` string pairs, optional (default `[]`)

**Response** — `Content-Type: text/event-stream`

SSE frames are sent in this order:

1. **Sources frame** (sent before LLM starts)
```
data: {"sources": [{"source": "data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf", "page": 2}]}
```

2. **Token frames** (one per token from Fireworks SSE stream)
```
data: {"token": "Hargurjeet"}
data: {"token": " has"}
data: {"token": " worked"}
...
```

3. **Done frame**
```
data: [DONE]
```

4. **Error frame** (if something goes wrong mid-stream)
```
data: {"error": "description of the error"}
data: [DONE]
```

**Error responses (non-SSE)**

| Status | Condition |
|--------|-----------|
| 500 | Vector store or LLM not loaded at startup |

**Example curl**
```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What cloud platforms has he used?", "chat_history": []}'
```

---

## Inactive Router

`api/routes/chat.py` defines a `/chat` router using `AsyncIteratorCallbackHandler` — the original HuggingFace Spaces implementation. It is **not mounted** in `api/main.py` and is not reachable. Do not rely on it.

## CORS

Wide-open: `allow_origins=["*"]`. Acceptable for a public portfolio chatbot. The Streamlit frontend communicates via `http://localhost:8000` (same container) so CORS is effectively bypassed in production.

## Fireworks API (upstream)

The backend calls Fireworks AI's OpenAI-compatible chat completions endpoint:

- **URL**: `https://api.fireworks.ai/inference/v1/chat/completions`
- **Model**: `accounts/fireworks/models/qwen3-8b`
- **Auth**: `Authorization: Bearer <FIREWORKS_API_KEY>`
- **Streaming**: `stream: true` with `Accept: text/event-stream`
- **Timeout**: 60 seconds

The custom `FireworksLLM` class (not using `openai` SDK) calls this directly with `requests`.

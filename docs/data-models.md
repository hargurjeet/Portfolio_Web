# Data Models & Configuration Reference

## API Request / Response Models

### ChatRequest (`api/main.py` inline, `api/schemas.py` for the inactive router)

```python
class ChatRequest(BaseModel):
    question: str
    chat_history: list = []   # list of [human_str, ai_str] pairs
```

`chat_history` is a flat list in `api/main.py` (passed as-is to `build_prompt`).  
The unused `api/schemas.py` defines it as `List[Tuple[str, str]]`.

### SSE Frame Shapes

All frames are JSON-encoded under `data: `.

| Frame type | Shape |
|------------|-------|
| Sources | `{"sources": [{"source": "filepath", "page": int_or_str}]}` |
| Token | `{"token": "string"}` |
| Error | `{"error": "message string"}` |
| Done | `[DONE]` (literal string, not JSON) |

### SourceDocument (schemas.py — unused)

```python
class SourceDocument(BaseModel):
    source: str
    page: int | str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
```

These models are defined but not used by the active `api/main.py` endpoint (which streams SSE directly).

## Configuration (`config.py`)

### Paths

| Constant | Value | Description |
|----------|-------|-------------|
| `DOCS_PATH` | `data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf` | Source PDF for index |
| `INDEX_PATH` | `faiss_index` | Directory for FAISS index files |

### Embedding

| Constant | Value | Description |
|----------|-------|-------------|
| `EMBEDDING_MODEL` | `all-mpnet-base-v2` | HuggingFace sentence-transformer model name |
| `EMBEDDING_DEVICE` | `cpu` | Device for inference |
| `NORMALIZE_EMBEDDINGS` | `True` | L2-normalise output embeddings |

### Chunking

| Constant | Value | Description |
|----------|-------|-------------|
| `CHUNK_SIZE` | `200` | Max characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between adjacent chunks |

Splitter separators (in priority order): `["\n\n", "\n", ".", " "]`

### Retrieval

| Constant | Value | Description |
|----------|-------|-------------|
| `TOP_K` | `4` | Number of documents retrieved per query |

Search type: `similarity` (cosine on normalised vectors = dot product).

### LLM (active)

| Constant | Value | Description |
|----------|-------|-------------|
| `FIREWORKS_MODEL` | `accounts/fireworks/models/qwen3-8b` | Active model |
| `FIREWORKS_TEMPERATURE` | `0.6` | Sampling temperature |
| `FIREWORKS_MAX_TOKENS` | `512` | Max tokens per response |
| `FIREWORKS_API_KEY` | from env | Loaded from `FIREWORKS_API_KEY` env var |

### LLM (stale — unused)

| Constant | Value | Note |
|----------|-------|------|
| `OPENAI_API_KEY` | from env | Not used anywhere active |
| `LLM_MODEL` | `gpt-5-nano` | Not used anywhere active |
| `LLM_TEMPERATURE` | `0.3` | Not used anywhere active |

## FireworksLLM Parameters

Full parameter set for `FireworksLLM` (in `core/fireworks_llm.py`):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model` | `accounts/fireworks/models/qwen3-8b` | Model identifier |
| `temperature` | `0.6` | Sampling temperature |
| `max_tokens` | `1024` | Max completion tokens (note: `config.py` sets 512, overrides this) |
| `top_p` | `1` | Nucleus sampling |
| `top_k` | `40` | Top-k sampling |
| `presence_penalty` | `0` | Presence penalty |
| `frequency_penalty` | `0` | Frequency penalty |
| `hide_think_blocks` | `True` | Strip `<think>...</think>` from Qwen3 output |
| `streaming` | `False` | LangChain streaming flag (not used for SSE path) |
| `api_key` | from env | Falls back to `FIREWORKS_API_KEY` if not set |

## System Prompt (`core/rag_chain.py`)

```
/no_think
You are a helpful assistant for Hargurjeet Singh Ganger's portfolio chatbot.
Use the context below to answer questions about his experience, skills, and background.
For conversational questions (like "what did I just ask?" or "can you elaborate?"),
use the chat history to respond naturally.
If you cannot answer from either the context or conversation history,
say "I don't have enough information to answer that."

Context from documents:
{context}
```

`/no_think` is a Qwen3-specific instruction to suppress chain-of-thought output. The think-block stripper in `stream_tokens()` provides a second layer of defence in case the model ignores the directive.

## HuggingFace Spaces Config (README frontmatter)

```yaml
title: Portfolio Website
emoji: 🚀
sdk: docker
app_port: 8501
```

`app_port: 8501` routes public traffic to the Streamlit process. FastAPI on 8000 remains internal.

## UI Content Data (hardcoded in `ui/streamlit_app.py`)

The following data is embedded directly in the Streamlit app (not from the database or API):

- **EXPERIENCE** list: 3 jobs (BT, Shell, TCS) with role, company, period, highlights, tags
- **EDUCATION** list: 3 entries (Liverpool JMU, IIIT Bangalore, VTU)
- **BLOGS** list: 27 blog posts with title, platform, URL, emoji
- **PROJECTS** list: 4 projects with title, description, banner URL, tags, GitHub URL, live URL, status
- **skills** list (topbar): 12 skill tags

To update any of this content, edit the corresponding list in `ui/streamlit_app.py`.

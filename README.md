---
title: Portfolio Website
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Streamlit template space
license: mit
---

# Portfolio Website - AI-Powered Chatbot 🤖

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive portfolio website featuring a production-ready RAG-powered conversational AI chatbot. Built with LangChain, FAISS, FastAPI, and Streamlit to showcase professional experience through intelligent document retrieval and natural language interactions.

## 🎯 Overview

This project demonstrates a complete end-to-end implementation of a Retrieval-Augmented Generation (RAG) system that:
- Ingests and processes PDF documents (resume/CV)
- Creates semantic embeddings using HuggingFace models
- Stores vectors in FAISS for efficient similarity search
- Provides real-time streaming responses via GPT-4o-mini
- Maintains conversational context across multiple turns
- Exposes both REST API and interactive web UI

## ✨ Features

### Core Capabilities
- **🤖 AI Chatbot**: Intelligent Q&A about professional experience, skills, and background
- **📚 RAG Pipeline**: Retrieval-Augmented Generation with FAISS vector store for accurate context retrieval
- **⚡ Streaming Responses**: Real-time token-by-token streaming for better UX
- **💬 Chat History**: Conversational memory for context-aware multi-turn dialogues
- **📄 Resume Viewer**: Embedded PDF viewer with download functionality
- **✍️ Blog Showcase**: Curated list of technical articles and publications
- **🚀 Projects Gallery**: Portfolio of deployed projects with live demos

### Technical Highlights
- Async streaming with FastAPI Server-Sent Events (SSE)
- Custom Streamlit UI with dark theme and responsive design
- Modular architecture for easy extension and maintenance
- Environment-based configuration management
- Error handling and graceful degradation

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **LangChain**: LLM orchestration and RAG pipeline
- **FAISS**: Facebook AI Similarity Search for vector storage
- **OpenAI GPT-4o-mini**: Language model for response generation
- **PyPDF**: PDF document parsing

### Frontend
- **Streamlit**: Interactive web application framework
- **Custom CSS**: Dark theme with modern UI/UX

### ML/AI
- **HuggingFace Transformers**: Sentence embeddings (all-mpnet-base-v2)
- **LangChain Community**: Document loaders and text splitters
- **Python-dotenv**: Environment variable management

## 📋 Prerequisites

- Python 3.12 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 2GB+ RAM for embedding model
- Internet connection for API calls

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/portfolio_website.git
cd portfolio_website
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

**Note**: Never commit your `.env` file. It's already in `.gitignore`.

### 5. Build Vector Store (First Time Only)
```bash
python main.py
```

This will:
- Load the PDF from `data/` directory
- Split it into chunks (1000 chars with 200 overlap)
- Generate embeddings using HuggingFace model
- Save FAISS index to `faiss_index/` directory

**Expected output**:
```
✅ Loaded 12 document(s)
✅ Split into 45 chunks
✅ Vector store saved to 'faiss_index'
```

### 6. Start the Backend API
```bash
uvicorn api.main:app --reload --port 8000
```

API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 7. Launch the Frontend
```bash
streamlit run ui/streamlit_app.py
```

Web app will open automatically at: http://localhost:8501

## 📁 Project Structure

```
portfolio_website/
│
├── api/                          # FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization
│   ├── schemas.py                # Pydantic models for request/response
│   └── routes/
│       ├── __init__.py
│       └── chat.py               # Chat endpoint with streaming
│
├── core/                         # RAG pipeline components
│   ├── __init__.py
│   ├── loader.py                 # Document loading (PDF, TXT)
│   ├── splitter.py               # Text chunking with overlap
│   ├── vector_store.py           # FAISS embedding & retrieval
│   └── rag_chain.py              # LLM chain with prompt engineering
│
├── data/                         # Source documents
│   └── Hargurjeet_Lead_GenAI_Specialist.pdf
│
├── faiss_index/                  # Vector database (generated)
│   ├── index.faiss               # FAISS index file
│   └── index.pkl                 # Document metadata
│
├── ui/                           # Streamlit frontend
│   └── streamlit_app.py          # Main UI with tabs (Chat, Resume, Blogs, Projects)
│
├── tests/                        # Unit tests (TODO)
│   └── __init__.py
│
├── .env                          # Environment variables (create this)
├── .gitignore                    # Git ignore rules
├── config.py                     # Centralized configuration
├── main.py                       # CLI chatbot for testing
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project metadata
├── uv.lock                       # Dependency lock file
├── LICENSE                       # MIT License
└── README.md                     # This file
```

## ⚙️ Configuration

Edit `config.py` to customize the RAG pipeline:

```python
# Paths
DOCS_PATH = "data/Hargurjeet_Lead_GenAI_Specialist.pdf"
INDEX_PATH = "faiss_index"

# Embedding model
EMBEDDING_MODEL = "all-mpnet-base-v2"  # 768-dim embeddings
EMBEDDING_DEVICE = "cpu"                # Use "cuda" for GPU
NORMALIZE_EMBEDDINGS = True

# Chunking strategy
CHUNK_SIZE = 1000                       # Characters per chunk
CHUNK_OVERLAP = 200                     # Overlap for context continuity

# Retrieval
TOP_K = 4                               # Number of relevant chunks to retrieve

# LLM
LLM_MODEL = "gpt-4o-mini"               # OpenAI model
LLM_TEMPERATURE = 0.3                   # Lower = more focused responses
```

### Recommended Settings

| Use Case | CHUNK_SIZE | CHUNK_OVERLAP | TOP_K | TEMPERATURE |
|----------|------------|---------------|-------|-------------|
| Technical docs | 1000 | 200 | 4 | 0.3 |
| Creative content | 800 | 150 | 3 | 0.7 |
| Short FAQs | 500 | 100 | 5 | 0.2 |

## 💻 Usage

### Web Interface (Recommended)

1. Navigate to http://localhost:8501
2. Use the **Chat** tab to ask questions
3. View **Resume** tab for embedded PDF
4. Explore **Blogs** and **Projects** tabs

**Example questions**:
- "What's Hargurjeet's experience with GenAI?"
- "Which cloud platforms has he worked with?"
- "Tell me about his most recent role"
- "What machine learning projects has he built?"

### REST API

**Endpoint**: `POST /api/v1/chat`

**Request**:
```json
{
  "question": "What's your experience with LangChain?",
  "chat_history": [
    ["What's your name?", "I'm Hargurjeet Singh Ganger"]
  ]
}
```

**Response** (Server-Sent Events):
```
data: {"token": "I"}
data: {"token": " have"}
data: {"token": " extensive"}
...
data: {"sources": [{"source": "resume.pdf", "page": 1}]}
data: [DONE]
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your key skills?", "chat_history": []}'
```

### CLI Mode

For quick testing without the web UI:

```bash
python main.py
```

```
🤖 RAG Pipeline ready! Type 'exit' to quit.

Ask a question: What's your experience with AWS?

💬 Answer:
I have extensive experience with AWS services including SageMaker, Lambda, Bedrock...

📄 Sources:
  [1] data/resume.pdf — page 1
  [2] data/resume.pdf — page 2
```

## 🔧 Advanced Configuration

### Using Different Embedding Models

```python
# In config.py
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Faster, smaller
# or
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # Higher quality
```

### GPU Acceleration

```python
# In config.py
EMBEDDING_DEVICE = "cuda"  # Requires CUDA-enabled GPU
```

### Using Different LLMs

```python
# In config.py
LLM_MODEL = "gpt-4"  # More capable but slower/expensive
# or
LLM_MODEL = "gpt-3.5-turbo"  # Faster and cheaper
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

### Test Chat Endpoint
```bash
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/v1/chat',
    json={'question': 'Hello', 'chat_history': []}
)
for line in response.iter_lines():
    print(line.decode())
"
```

## 🐛 Troubleshooting

### Issue: "Vector store not loaded"
**Solution**: Run `python main.py` first to build the FAISS index.

### Issue: "Could not connect to API"
**Solution**: Ensure FastAPI is running on port 8000: `uvicorn api.main:app --reload`

### Issue: "OpenAI API key not found"
**Solution**: Check `.env` file exists and contains `OPENAI_API_KEY=your_key`

### Issue: "Out of memory"
**Solution**: Reduce `CHUNK_SIZE` or use a smaller embedding model.

### Issue: Slow embedding generation
**Solution**: Use GPU acceleration or switch to a smaller model like `all-MiniLM-L6-v2`.

## 📊 Performance Metrics

- **Embedding Generation**: ~2-3 seconds for 50 chunks (CPU)
- **Query Response Time**: ~1-2 seconds (streaming starts immediately)
- **Vector Search**: <100ms for similarity search
- **Memory Usage**: ~500MB (embedding model + FAISS index)

## 🔒 Security Considerations

- ✅ API keys stored in `.env` (not committed)
- ✅ Input validation via Pydantic schemas
- ✅ CORS configured for production
- ⚠️ Add authentication for production deployment
- ⚠️ Implement rate limiting for API endpoints

## 🚀 Deployment

### Docker

**Build and run with Docker Compose** (Recommended):
```bash
# Set your OpenAI API key in .env file first
docker-compose up --build
```

**Or build and run manually**:
```bash
# Build image
docker build -t portfolio-chatbot .

# Run container
docker run -p 8000:8000 -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  portfolio-chatbot
```

Access:
- **Streamlit UI**: http://localhost:8501
- **FastAPI**: http://localhost:8000/docs

### Cloud Platforms
- **AWS**: Deploy on EC2 or ECS with Application Load Balancer
- **GCP**: Use Cloud Run for serverless deployment
- **Azure**: Deploy on App Service or Container Instances
- **Streamlit Cloud**: Deploy UI directly from GitHub

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Hargurjeet Singh Ganger**
- LinkedIn: [linkedin.com/in/hargurjeet](https://linkedin.com/in/hargurjeet)
- GitHub: [github.com/hargurjeet](https://github.com/hargurjeet)
- Medium: [gurjeet333.medium.com](https://gurjeet333.medium.com)
- Email: gurjeet333@gmail.com

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the RAG framework
- [OpenAI](https://openai.com/) for GPT models
- [HuggingFace](https://huggingface.co/) for embedding models
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Streamlit](https://streamlit.io/) for the frontend framework

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FAISS Documentation](https://faiss.ai/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

⭐ **Star this repo** if you find it helpful!

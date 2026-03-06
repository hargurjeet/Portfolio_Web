import os
from dotenv import load_dotenv

load_dotenv()

# Paths
DOCS_PATH = "data/Hargurjeet_Singh_Ganger_KnowledgeBase.pdf"
INDEX_PATH = "faiss_index"

# Embedding model
EMBEDDING_MODEL = "all-mpnet-base-v2"
EMBEDDING_DEVICE = "cpu"
NORMALIZE_EMBEDDINGS = True

# Chunking
CHUNK_SIZE = 200
CHUNK_OVERLAP = 50

# Retrieval
TOP_K = 4

# LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-5-nano"
LLM_TEMPERATURE = 0.3

FIREWORKS_MODEL = "accounts/fireworks/models/qwen3-8b"
FIREWORKS_TEMPERATURE = 0.6
FIREWORKS_MAX_TOKENS = 1024
FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY')
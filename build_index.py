import os
import sys

sys.path.insert(0, "/app")

from core.loader import load_documents
from core.splitter import split_documents
from core.vector_store import create_vector_store
from config import DOCS_PATH, INDEX_PATH

print("Building FAISS index...")
docs = load_documents(DOCS_PATH)
chunks = split_documents(docs)
create_vector_store(chunks, INDEX_PATH)
print("Index built successfully")
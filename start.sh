#!/bin/bash
set -e

echo "Starting Portfolio Chatbot..."

if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index)" ]; then
    echo "Building FAISS index..."
    python -c "
from core.loader import load_documents
from core.splitter import split_documents
from core.vector_store import create_vector_store
from config import DOCS_PATH, INDEX_PATH
docs = load_documents(DOCS_PATH)
chunks = split_documents(docs)
create_vector_store(chunks, INDEX_PATH)
print(chr(39)+Index
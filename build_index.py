import os
import sys

sys.path.insert(0, "/app")


print("build_index.py: starting...", flush=True)

from config import DOCS_PATH, INDEX_PATH
print(f"build_index.py: DOCS_PATH={DOCS_PATH}, INDEX_PATH={INDEX_PATH}", flush=True)

from core.loader import load_documents
print("build_index.py: loading documents...", flush=True)
docs = load_documents(DOCS_PATH)
print(f"build_index.py: loaded {len(docs)} docs", flush=True)

from core.splitter import split_documents
print("build_index.py: splitting documents...", flush=True)
chunks = split_documents(docs)
print(f"build_index.py: split into {len(chunks)} chunks", flush=True)

from core.vector_store import create_vector_store
print("build_index.py: creating vector store (embedding model loads here)...", flush=True)
create_vector_store(chunks, INDEX_PATH)
print("build_index.py: done!", flush=True)
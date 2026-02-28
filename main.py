import logging
import warnings
import hashlib

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

import os
from config import DOCS_PATH, INDEX_PATH
from core.loader import load_documents
from core.splitter import split_documents
from core.vector_store import create_vector_store, load_vector_store
from core.rag_chain import ask

def get_docs_hash(docs_path):
    """Hash all filenames + modified times to detect changes."""
    files = sorted(
        (f, os.path.getmtime(os.path.join(docs_path, f)))
        for f in os.listdir(docs_path)
    )
    return hashlib.md5(str(files).encode()).hexdigest()

HASH_FILE = os.path.join(INDEX_PATH, "docs_hash.txt")

def index_is_stale():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(HASH_FILE):
        return True
    with open(HASH_FILE) as f:
        old_hash = f.read().strip()
    return old_hash != get_docs_hash(DOCS_PATH)

def save_docs_hash():
    os.makedirs(INDEX_PATH, exist_ok=True)
    with open(HASH_FILE, "w") as f:
        f.write(get_docs_hash(DOCS_PATH))

def main():
    if index_is_stale():
        print(f"Docs changed or no index found — rebuilding from: {DOCS_PATH}")
        docs = load_documents(DOCS_PATH)
        chunks = split_documents(docs)
        vector_store = create_vector_store(chunks, INDEX_PATH)
    else:
        vector_store = load_vector_store(INDEX_PATH)

    print("\n🤖 RAG Pipeline ready! Type 'exit' to quit.\n")
    chat_history = []
    while True:
        question = input("Ask a question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if question:
            result = ask(vector_store, question, chat_history)
            # Update history for next turn
            chat_history.append([question, result["answer"]])


if __name__ == "__main__":
    main()
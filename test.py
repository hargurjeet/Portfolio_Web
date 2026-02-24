# rag_pipeline.py
import logging
import warnings

# suppress sentence-transformers logs
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()



# ── 1. LOAD DOCUMENTS ──────────────────────────────────────────────────────────
def load_documents(path: str):
    """
    Load PDFs from a file path or a folder.
    Supports .pdf and .txt files.
    """
    if os.path.isdir(path):
        # Load all PDFs in a directory
        loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    elif path.endswith(".pdf"):
        loader = PyPDFLoader(path)
    elif path.endswith(".txt"):
        loader = TextLoader(path)
    else:
        raise ValueError("Unsupported file type. Use .pdf or .txt")

    documents = loader.load()
    print(f"✅ Loaded {len(documents)} document(s)")
    return documents


# ── 2. SPLIT INTO CHUNKS ───────────────────────────────────────────────────────
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # characters per chunk
        chunk_overlap=200,    # overlap to preserve context
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks


# ── 3. CREATE VECTOR STORE ─────────────────────────────────────────────────────
def create_vector_store(chunks, save_path="faiss_index"):
    """
    Embed chunks using Gemini embeddings and store in FAISS.
    Saves index to disk so you don't re-embed every run.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="all-mpnet-base-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(save_path)
    print(f"✅ Vector store saved to '{save_path}'")
    return vector_store


def load_vector_store(save_path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-mpnet-base-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vector_store = FAISS.load_local(
        save_path, embeddings, allow_dangerous_deserialization=True
    )
    return vector_store


# ── 4. BUILD RAG CHAIN ─────────────────────────────────────────────────────────
def build_rag_chain(vector_store):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt_template = """
    You are a helpful assistant. Use the context below to answer the question.
    If you don't know the answer from the context, say "I don't have enough information to answer that."

    Context:
    {context}

    Question: {question}

    Answer:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}  # retrieve top 4 chunks
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return rag_chain


# ── 5. QUERY ───────────────────────────────────────────────────────────────────
def ask(chain, question: str):
    print(f"\n🔍 Question: {question}")
    result = chain.invoke({"query": question})
    
    print(f"\n💬 Answer:\n{result['result']}")
    
    print("\n📄 Sources:")
    for i, doc in enumerate(result["source_documents"]):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        print(f"  [{i+1}] {source} — page {page}")
    
    return result


# ── 6. MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    INDEX_PATH = "faiss_index"
    DOCS_PATH = "/Users/hargurjeetsinghganger/Documents/programming/portfolio_website/chatbot/data/resume.pdf"  # 👈 put your PDFs in this folder

    # Build index if it doesn't exist, otherwise load from disk
    if not os.path.exists(INDEX_PATH):
        docs = load_documents(DOCS_PATH)
        chunks = split_documents(docs)
        vector_store = create_vector_store(chunks, INDEX_PATH)
    else:
        vector_store = load_vector_store(INDEX_PATH)

    chain = build_rag_chain(vector_store)

    # Interactive loop
    print("\n🤖 RAG Pipeline ready! Type 'exit' to quit.\n")
    while True:
        question = input("Ask a question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if question:
            ask(chain, question)
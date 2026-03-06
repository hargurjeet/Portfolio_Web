from core.fireworks_llm import FireworksLLM
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from config import FIREWORKS_API_KEY, FIREWORKS_MODEL, FIREWORKS_TEMPERATURE, FIREWORKS_MAX_TOKENS, TOP_K


def build_llm(streaming: bool = False, callbacks: list = [], hide_think_blocks: bool = True):
    """Build Fireworks LLM instance"""
    return FireworksLLM(
        model=FIREWORKS_MODEL,
        temperature=FIREWORKS_TEMPERATURE,
        max_tokens=FIREWORKS_MAX_TOKENS,
        api_key=FIREWORKS_API_KEY,
        streaming=streaming,
        callbacks=callbacks,
        hide_think_blocks=hide_think_blocks
    )


def retrieve_docs(vector_store, question: str):
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K}
    )
    return retriever.invoke(question)


def build_prompt(question: str, context: str, chat_history: list) -> list:
    """
    Build messages list with system prompt, history, and current question.
    chat_history: list of [human, ai] pairs
    """
    system = """You are a helpful assistant for Hargurjeet Singh Ganger's portfolio chatbot.
Use the context below to answer questions about his experience, skills, and background.
For conversational questions (like "what did I just ask?" or "can you elaborate?"),
use the chat history to respond naturally.
If you cannot answer from either the context or conversation history,
say "I don't have enough information to answer that."

Context from documents:
{context}"""

    messages = [{"role": "system", "content": system.format(context=context)}]

    # Inject prior turns
    for human, ai in chat_history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": ai})

    # Add current question
    messages.append({"role": "user", "content": question})
    return messages


def ask(vector_store, question: str, chat_history: list = []):
    """For terminal use via main.py"""
    print(f"\n🔵 [RAG] ask() called with question: {question}")
    print(f"🔵 [RAG] Chat history length: {len(chat_history)}")
    
    # Check if vector_store is valid
    print(f"🔵 [RAG] Vector store type: {type(vector_store)}")
    
    docs = retrieve_docs(vector_store, question)
    print(f"🔵 [RAG] Retrieved {len(docs)} documents")
    
    if len(docs) == 0:
        print("🔴 [RAG] No documents retrieved!")
    
    context = "\n\n".join(doc.page_content for doc in docs)
    print(f"🔵 [RAG] Context length: {len(context)} characters")
    print(f"🔵 [RAG] Context preview: {context[:200]}...")
    
    messages = build_prompt(question, context, chat_history)
    print(f"🔵 [RAG] Built prompt with {len(messages)} messages")
    print(f"🔵 [RAG] Last message: {messages[-1]}")

    llm = build_llm()
    print(f"🔵 [RAG] LLM created: {type(llm)}")
    
    try:
        response = llm.invoke(messages)
        print(f"🔵 [RAG] LLM response type: {type(response)}")
        print(f"🔵 [RAG] LLM response preview: {str(response)[:200]}")
        print(f"🔵 [RAG] LLM response length: {len(str(response))}")
        
        if not response:
            print("🔴 [RAG] Empty response from LLM!")
            response = "I couldn't generate a response at this time."
            
    except Exception as e:
        print(f"🔴 [RAG] Error in LLM invoke: {str(e)}")
        import traceback
        traceback.print_exc()
        response = f"Error generating response: {str(e)}"

    print(f"\n💬 Answer:\n{response}")
    print("\n📄 Sources:")
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        print(f"  [{i+1}] {source} — page {page}")

    return {"answer": response, "source_documents": docs}
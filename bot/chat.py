import ollama
import time
from bot.prompts import ACTIVE_PROMPT
from rag.retriever import retrieve

def chat(user_message, history, use_rag=True, model_key="minilm"):
    context = retrieve(user_message, top_k=4, model_key=model_key) if use_rag else ""
    full_msg = (
        f"Context from Duke knowledge base:\n\n{context}\n\n---\n\nStudent question: {user_message}"
        if context else user_message
    )
    messages = [{"role": "system", "content": ACTIVE_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": full_msg})

    start = time.time()
    response = ollama.chat(model="llama3.2", messages=messages)
    latency = time.time() - start

    reply = response["message"]["content"]
    clean_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]
    return reply, clean_history, latency, context

def reset_conversation():
    return []
import ollama
import time
from bot.prompts import ACTIVE_PROMPT
from rag.retriever import retrieve

# Most content in this file generated with AI, using Claude Sonnet 4.6

MAX_TURNS_BEFORE_SUMMARY = 6  # summarize after this many messages in history

def summarize_history(history: list[dict]) -> str:
    """
    Summarize conversation history to manage context window size.
    Instead of passing all previous messages, we compress them into
    a short summary that preserves key facts discussed.
    """
    if not history:
        return ""
    
    conversation_text = ""
    for msg in history:
        role = "Student" if msg["role"] == "user" else "DukeBot"
        conversation_text += f"{role}: {msg['content']}\n"
    
    summary_prompt = (
        "Summarize the following conversation in 2-3 sentences, "
        "keeping only the most important facts and questions discussed:\n\n"
        + conversation_text
    )
    
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response["message"]["content"]


def chat(user_message, history, use_rag=True, model_key="minilm"):
    context = retrieve(user_message, top_k=4, model_key=model_key) if use_rag else ""
    full_msg = (
        f"Context from Duke knowledge base:\n\n{context}\n\n---\n\nStudent question: {user_message}"
        if context else user_message
    )

    # Context management: if history is long, summarize it instead of
    # passing everything — this prevents the context window from growing
    # unbounded and keeps responses focused
    if len(history) >= MAX_TURNS_BEFORE_SUMMARY:
        summary = summarize_history(history)
        compressed_history = [{
            "role": "user",
            "content": f"[Summary of our conversation so far: {summary}]"
        }, {
            "role": "assistant", 
            "content": "Understood, I have the context from our previous conversation."
        }]
    else:
        compressed_history = history

    messages = [{"role": "system", "content": ACTIVE_PROMPT}]
    messages += compressed_history
    messages.append({"role": "user", "content": full_msg})

    start = time.time()
    response = ollama.chat(model="llama3.2", messages=messages)
    latency = time.time() - start

    reply = response["message"]["content"]

    # Always append to full history so we have the complete record
    # (we only compress what we send to the model, not what we store)
    clean_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]
    return reply, clean_history, latency, context


def reset_conversation():
    return []
import os
import time
import requests
from .prompts import ACTIVE_PROMPT      
from src.rag.retriever import retrieve
# Most content in this file generated with AI, using Claude Sonnet 4.6

GROQ_TOKEN = os.environ.get("GROQ_API_KEY")
# GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_MODEL = "llama-3.3-70B-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_TURNS_BEFORE_SUMMARY = 6


def _hf_generate(messages: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    if not response.ok:
        raise ValueError(f"Groq API error {response.status_code}: {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()


def summarize_history(history: list[dict]) -> str:
    if not history:
        return ""
    conversation_text = ""
    for msg in history:
        role = "Student" if msg["role"] == "user" else "DukeBot"
        conversation_text += f"{role}: {msg['content']}\n"
    messages = [{"role": "user", "content": f"Summarize this conversation in 2-3 sentences:\n\n{conversation_text}"}]
    return _hf_generate(messages)


def chat(user_message, history, use_rag=True, model_key="minilm"):
    context = retrieve(user_message, top_k=4, model_key=model_key) if use_rag else ""
    full_msg = (
        f"Context from Duke knowledge base:\n\n{context}\n\n---\n\nStudent question: {user_message}"
        if context else user_message
    )

    if len(history) >= MAX_TURNS_BEFORE_SUMMARY:
        summary = summarize_history(history)
        compressed_history = [
            {"role": "user", "content": f"[Summary of our conversation so far: {summary}]"},
            {"role": "assistant", "content": "Understood."}
        ]
    else:
        compressed_history = history

    messages = [{"role": "system", "content": ACTIVE_PROMPT}]
    messages += compressed_history
    messages.append({"role": "user", "content": full_msg})

    start = time.time()
    reply = _hf_generate(messages)
    latency = time.time() - start

    clean_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]
    return reply, clean_history, latency, context


def reset_conversation():
    return []
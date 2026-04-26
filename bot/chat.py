import os
import time
import requests
from bot.prompts import ACTIVE_PROMPT
from rag.retriever import retrieve

# Most content in this file generated with AI, using Claude Sonnet 4.6

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}/v1/chat/completions"

MAX_TURNS_BEFORE_SUMMARY = 6


def _hf_generate(messages: list[dict]) -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": HF_MODEL,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7,
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    if not response.ok:
        raise ValueError(f"HF API error {response.status_code}: {response.text}")
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
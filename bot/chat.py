import os
import time
import requests
from bot.prompts import ACTIVE_PROMPT
from rag.retriever import retrieve

# Most content in this file generated with AI, using Claude Sonnet 4.6

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

MAX_TURNS_BEFORE_SUMMARY = 6


def _hf_generate(prompt_text: str) -> str:
    """Call HuggingFace Inference API with a plain text prompt."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "return_full_text": False,
        }
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, list):
        return result[0].get("generated_text", "").strip()
    return str(result)


def _build_prompt(system: str, messages: list[dict], user_message: str) -> str:
    """
    Format messages into Mistral's instruction format:
    <s>[INST] system + user [/INST] assistant </s>[INST] user [/INST]
    """
    prompt = f"<s>[INST] {system}\n\n"
    for msg in messages:
        if msg["role"] == "user":
            prompt += f"{msg['content']} [/INST] "
        elif msg["role"] == "assistant":
            prompt += f"{msg['content']} </s><s>[INST] "
    prompt += f"{user_message} [/INST]"
    return prompt


def summarize_history(history: list[dict]) -> str:
    """Summarize conversation history to manage context window size."""
    if not history:
        return ""
    conversation_text = ""
    for msg in history:
        role = "Student" if msg["role"] == "user" else "DukeBot"
        conversation_text += f"{role}: {msg['content']}\n"
    summary_prompt = (
        "<s>[INST] Summarize the following conversation in 2-3 sentences, "
        "keeping only the most important facts and questions discussed:\n\n"
        + conversation_text + " [/INST]"
    )
    return _hf_generate(summary_prompt)


def chat(user_message, history, use_rag=True, model_key="minilm"):
    context = retrieve(user_message, top_k=4, model_key=model_key) if use_rag else ""
    full_msg = (
        f"Context from Duke knowledge base:\n\n{context}\n\n---\n\nStudent question: {user_message}"
        if context else user_message
    )

    # Context management: summarize if history is long
    if len(history) >= MAX_TURNS_BEFORE_SUMMARY:
        summary = summarize_history(history)
        compressed_history = [
            {"role": "user", "content": f"[Summary of our conversation so far: {summary}]"},
            {"role": "assistant", "content": "Understood, I have the context from our previous conversation."}
        ]
    else:
        compressed_history = history

    # Build prompt in Mistral format
    prompt = _build_prompt(ACTIVE_PROMPT, compressed_history, full_msg)

    start = time.time()
    reply = _hf_generate(prompt)
    latency = time.time() - start

    clean_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]
    return reply, clean_history, latency, context


def reset_conversation():
    return []
"""
rag/embedder.py
Embeds text chunks using two different sentence-transformer models and compares them.
The model comparison is the second technique for the 10-pt custom RAG rubric item.
Also covers the 5-pt "sentence embeddings for semantic similarity/retrieval" item.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# Two models to compare — this is your "embedding model comparison" technique
MODEL_OPTIONS = {
    "minilm": "all-MiniLM-L6-v2",       # Fast, small, good general purpose
    "mpnet": "all-mpnet-base-v2",         # Slower, larger, better quality
}

_loaded_models = {}


def get_model(model_key: str) -> SentenceTransformer:
    if model_key not in _loaded_models:
        print(f"Loading embedding model: {MODEL_OPTIONS[model_key]}")
        _loaded_models[model_key] = SentenceTransformer(MODEL_OPTIONS[model_key])
    return _loaded_models[model_key]


def embed_texts(texts: list[str], model_key: str = "minilm") -> np.ndarray:
    """Embed a list of texts using the specified model."""
    model = get_model(model_key)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings


def compare_models_on_query(query: str, corpus: list[str]) -> dict:
    """
    Compare retrieval results from both embedding models on the same query.
    Used in eval/evaluate.py to document model comparison for rubric evidence.
    
    Returns top-3 results from each model.
    """
    results = {}
    for key in MODEL_OPTIONS:
        q_emb = embed_texts([query], model_key=key)
        c_emb = embed_texts(corpus, model_key=key)
        scores = (q_emb @ c_emb.T)[0]
        top_indices = np.argsort(scores)[::-1][:3]
        results[key] = [(corpus[i], float(scores[i])) for i in top_indices]
    return results

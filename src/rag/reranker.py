"""
rag/reranker.py
Cross-encoder reranking of retrieved chunks.
This is the third technique for the custom RAG pipeline rubric item,
alongside custom chunking and embedding model comparison.
"""

from sentence_transformers import CrossEncoder

_model = None

def get_reranker():
    global _model
    if _model is None:
        print("Loading reranker model...")
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _model

def rerank(query: str, docs: list[str], top_k: int = 3) -> list[str]:
    """
    Rerank a list of retrieved docs using a cross-encoder.
    More accurate than embedding similarity alone — the cross-encoder
    sees the query and document together rather than separately.
    """
    reranker = get_reranker()
    pairs = [(query, doc) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), reverse=True)
    return [doc for _, doc in ranked[:top_k]]
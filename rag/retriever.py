import os
import chromadb
from rag.chunker import load_and_chunk_all
from rag.embedder import embed_texts
from rag.reranker import rerank

# Most content in this file generated with AI, using Claude Sonnet 4.6

DB_PATH = "./chroma_db"
DATA_DIR = "./data/duke_docs"


def _collection_name(model_key: str) -> str:
    return f"duke_knowledge_{model_key}"


def build_index(model_key: str = "minilm") -> chromadb.Collection:
    client = chromadb.PersistentClient(path=DB_PATH)
    col_name = _collection_name(model_key)
    try:
        client.delete_collection(col_name)
    except Exception:
        pass
    collection = client.create_collection(col_name)
    chunks = load_and_chunk_all(DATA_DIR)
    print(f"Indexing {len(chunks)} chunks with {model_key}...")
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]
    embeddings = embed_texts(texts, model_key=model_key)
    collection.add(documents=texts, embeddings=embeddings.tolist(), ids=ids, metadatas=metadatas)
    print("Index built.")
    return collection


def get_collection(model_key: str = "minilm") -> chromadb.Collection:
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        return client.get_collection(_collection_name(model_key))
    except Exception:
        return build_index(model_key=model_key)


def retrieve(query: str, top_k: int = 4, model_key: str = "minilm") -> str:
    collection = get_collection(model_key)
    query_embedding = embed_texts([query], model_key=model_key)[0].tolist()
    
    # Fetch more candidates than needed, then rerank down to top_k
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 3,  # over-fetch for reranking
        include=["documents", "metadatas", "distances"]
    )
    
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    
    # Rerank using cross-encoder
    reranked_docs = rerank(query, docs, top_k=top_k)
    
    # Match metadata back to reranked docs
    doc_to_meta = {doc: meta for doc, meta in zip(docs, metas)}
    
    parts = []
    for doc in reranked_docs:
        meta = doc_to_meta.get(doc, {"source": "unknown"})
        parts.append(f"[Source: {meta['source']}]\n{doc}")
    return "\n\n---\n\n".join(parts)
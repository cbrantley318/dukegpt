import os
import chromadb
from rag.chunker import load_and_chunk_all
from rag.embedder import embed_texts

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
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        parts.append(f"[Source: {meta['source']}]\n{doc}")
    return "\n\n---\n\n".join(parts)
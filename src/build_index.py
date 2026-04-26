"""
build_index.py
Run this once before starting the app to build the ChromaDB vector index.

    python build_index.py
"""

# Most content in this file generated with AI, using Claude Sonnet 4.6

from src.rag.retriever import build_index
if __name__ == "__main__":
    print("Building index with MiniLM (fast)...")
    build_index(model_key="minilm")
    print("\nBuilding index with MPNet (accurate)...")
    build_index(model_key="mpnet")
    print("\nDone! Both indexes are ready.")

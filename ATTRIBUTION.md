# Attribution

## AI Tool Usage

This project used Claude (via claude.ai) as a development assistant throughout the project.

### What was AI-generated
- Initial scaffolding for `app.py`, `bot/chat.py`, `rag/chunker.py`, `rag/embedder.py`, and `rag/retriever.py` was generated with Claude's assistance.
- The evaluation script structure in `eval/evaluate.py` was drafted with AI assistance.

### What we modified
- The chunking strategy in `chunker.py` was tuned by us — we adjusted `chunk_size` and `overlap` parameters after observing retrieval quality on real Duke documents.
- The reward/system prompt in `bot/prompts.py` was iteratively refined by us after testing the three variants.
- The observation processing and embedding comparison logic were substantially reworked after the initial scaffold didn't handle ChromaDB's API correctly.

### What we debugged and reworked
- ChromaDB's persistent client API changed between versions; we had to fix collection initialization.
- The context injection approach in `chat.py` (injecting context into user turn vs. system prompt) was a design decision we made ourselves after testing both approaches.
- The multi-index approach (separate indexes per model key) was our own solution to support runtime model switching in the Streamlit UI.

## External Sources
- [Anthropic Python SDK documentation](https://docs.anthropic.com)
- [Sentence Transformers documentation](https://www.sbert.net/)
- [ChromaDB documentation](https://docs.trychroma.com/)
- [Streamlit documentation](https://docs.streamlit.io/)
- Duke University website content used for knowledge base documents (duke.edu, library.duke.edu, studentaffairs.duke.edu, dining.duke.edu)

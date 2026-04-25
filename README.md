# DukeBot — AI Student Assistant

## What it Does

DukeBot is an AI-powered assistant for Duke University students. It answers questions about campus life — dining hours, library hours, academic deadlines, health resources, and more — by combining the Claude language model with a custom Retrieval-Augmented Generation (RAG) pipeline built on Duke-specific documents. Students can ask questions in natural language through a Streamlit web interface, and DukeBot retrieves relevant information from its Duke knowledge base before generating a grounded, accurate response.

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
python build_index.py
streamlit run app.py
```

See [SETUP.md](SETUP.md) for full installation instructions.

## Video Links

- **Demo video**: [link]
- **Technical walkthrough**: [link]

## Evaluation

### Quantitative Results

| Metric | Iteration 1 (MiniLM) | Iteration 2 (MPNet) |
|---|---|---|
| Answer accuracy (keyword hit rate) | TBD | TBD |
| Mean response latency | TBD | TBD |
| Retrieval coverage | TBD | TBD |

Run `python -m eval.evaluate` to reproduce these results. Full plots in `eval/figures/`.

### Qualitative Outcomes

DukeBot handles factual questions about campus resources well when the relevant document is in the knowledge base. It appropriately declines to answer questions outside its knowledge base (e.g., live sports scores, weather) rather than hallucinating. See `eval/error_analysis.json` for documented failure cases.

## Individual Contributions

- **Partner 1 [name]**: RAG pipeline (chunker, embedder, retriever), evaluation script, build_index.py
- **Partner 2 [name]**: Streamlit UI, prompt engineering, documentation, demo/walkthrough videos

## Design Decisions

**Why Claude API over a local model?** We evaluated local models (Llama 3.1 8B via Ollama) against the Claude API. Claude produced more accurate, better-formatted responses and required no GPU for inference. The tradeoff is cost (~$0.002/query) and an external dependency, but for a student assistant with moderate usage this is acceptable.

**Why sentence-transformers over OpenAI embeddings?** Sentence-transformers run locally (no additional API cost), are fast enough for our use case, and we compared two variants (MiniLM vs MPNet) to empirically select the better-performing model.

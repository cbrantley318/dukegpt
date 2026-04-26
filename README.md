# DukeBot — AI Student Assistant

## What it Does

DukeBot is an AI-powered assistant for Duke University students. It answers questions about campus life — dining hours, library hours, academic deadlines, health resources, and more — by combining the Claude language model with a custom Retrieval-Augmented Generation (RAG) pipeline built on Duke-specific documents. Students can ask questions in natural language through a Streamlit web interface, and DukeBot retrieves relevant information from its Duke knowledge base before generating a grounded, accurate response.

## Quick Start

Run the following from the top-level directory

```bash
pip install -r requirements.txt
python src/build_index.py
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

- **Partner 1 [Carson]**: RAG pipeline (chunker, embedder, retriever), web scraping
- **Partner 2 [Joyce]**: Streamlit UI, prompt engineering, documentation, demo/walkthrough videos, evaluation script, build_index.py


## Design Decisions

Initially, this project used a local Ollama instance to run Llama3.2 on the host machine. However, we eventually migrated to using Groq's API to access a remote model (coincidentally, this currently also uses Llama3.2, but we did experiment with DeepSeek, Openai and others). These two ML approaches both yield comparable results in terms of accuracy and the outputted tokens, but differ largely in the host machine's computational requirements and inference latency. As shown earlier in the results section, using the local model leads to an average response latency of about 4.8 seconds, almost 7x greater than when using an API for remote computation. 

Additionally, integrating an API enabled the platform to be deployed to the public. While the local machine was able to host its own server and be accessed by other devices (using ngrok), this put higher load on the host machine (my laptop) and required it to be on. A dedicated server has close to 100% uptime and is able to handle multiple requests, and using Streamlit does not allow for as much heavy computation at the host server (as running Ollama is its own process and acts like a server on the host machine), making Ollama largely incompatible with deployment. However, by integrating the project with a public API, it is able to be deployed and maintain fast response times that weren't achievable with a local model running on a commercial processor and GPU. 

This came with the added difficulty of integrating Groq's API into the system. The only file that needed to be changed to accomplish this was bot/chat.py, along with the addition of some environment variables / secret keys. Initially we tried using the Huggingface Inference API for this task, but it recently rebranded and dropped support for many of the models it provided, leading us to use Groq instead.


# Attribution

## AI Tool Usage

This project used Claude (via claude.ai) as a development assistant throughout the project.

### What was AI-generated
- Initial scaffolding for `app.py`, `bot/chat.py`, `rag/chunker.py`, `rag/embedder.py`, and `rag/retriever.py` was generated with Claude's assistance.
- Web_scraper.py partially generated with Claude Sonnet 4.6
- The evaluation script structure in `eval/evaluate.py` was drafted with AI assistance.

### What we modified
- The chunking strategy in `chunker.py` was tuned by us — we adjusted `chunk_size` and `overlap` parameters after observing retrieval quality on real Duke documents.
- The reward/system prompt in `bot/prompts.py` was refined and tuned by us after testing the three variants.

### What we debugged and reworked
- Added context management and history tracking that wasn't including in the code produced by Claude
- Modified the web scraping script to ignore duplicate links (i.e. crawling two different websites that both have a link to the same website)
- Reworked how it stores the files retrieved for RAG

## Data sources
- Data was scraped from various duke.edu subdomains, including dining.duke.edu, students.duke.edu, and financialaid.duke.edu

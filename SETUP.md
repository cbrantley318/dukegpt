# Setup Instructions

## Prerequisites
- Python 3.10 or higher
- An Anthropic API key (get one at console.anthropic.com — add $5 credit, will cost ~$1-3 total)

## Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd dukegpt

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure Ollama is installed properly (see ollama website for windows, linux/Mac command shown below)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

## Adding Duke Documents

Place any txt docs you want for specific information retrieval
Otherwise, run (from the dukegpt dir) the following: python src/web_scrape.py
To collect information from the internet
If you like, modify DUKE_SEEDS in src/web_scrape.py to add/remove domains to scrape from

## Build the Knowledge Index

```bash
python build_index.py
```

This only needs to run once (or when you add new documents).

## Run the App

```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501.

## Run Evaluation

```bash
python -m eval.evaluate
```

Results are saved to `eval/figures/` and `eval/*.json`.

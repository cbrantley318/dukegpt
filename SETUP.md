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

# 4. Set your API key
# export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# On Windows: set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Adding Duke Documents

Place `.txt` files in `data/duke_docs/`. Each file should contain plain text
copied from Duke websites (dining hours, library hours, academic calendar, etc.).
Three sample files are already included.

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

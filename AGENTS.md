# AGENTS.md

Notes for AI coding agents working on this project.

## Setup

```
pip install -r requirements.txt
cp .env.example .env
# then fill in .env with real keys (mem0, Firecrawl, Langfuse)
```

Requires Ollama running locally with a model pulled (default: `llama3.1`).

## Run

```
python3 assistant.py
```

## Test

There is no automated test suite yet. To manually verify a change works:

1. Run `python3 assistant.py`
2. Send a plain message and confirm you get a reply from the local model
3. Send a message referencing something told to it in an earlier session and confirm mem0 recall works
4. Send a message containing a URL and confirm Firecrawl fetches and summarizes it
5. Check the Langfuse dashboard and confirm the run appears with steps, tokens, and cost

## Quirks

- `OLLAMA_URL` and `MODEL` are hardcoded constants at the top of `assistant.py`, not environment variables — edit them directly to change the model.
- The script is a single file (`assistant.py`); there's no package structure yet.
- `.env` holds real secrets and is gitignored — never commit it. `.env.example` is the template to keep in sync when new environment variables are added.

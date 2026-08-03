# My Assistant

A small, local-first AI assistant. It runs entirely on your own machine using [Ollama](https://ollama.com), and can be extended with memory, live web access, and observability.

## What it does

- Chats with you in the terminal using a local Ollama model (`llama3.1` by default)
- Remembers facts about you across separate sessions, using [mem0](https://mem0.ai)
- Reads live web pages when you paste a URL into a message, using [Firecrawl](https://firecrawl.dev)
- Logs every run (steps, tokens, cost) to [Langfuse](https://langfuse.com) so you can see what it did

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed and running locally, with a model pulled (e.g. `ollama pull llama3.1`)
- Free API keys for [mem0](https://mem0.ai), [Firecrawl](https://firecrawl.dev), and [Langfuse](https://langfuse.com)

## Install

```
pip install -r requirements.txt
```

## Configure

Copy the example environment file and fill in your own keys:

```
cp .env.example .env
```

Edit `.env` with your own `MEM0_API_KEY`, `MEM0_USER_ID`, `FIRECRAWL_API_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_HOST`.

## Run

```
python3 assistant.py
```

Type a message and press enter. Type `exit` to quit.

## License

MIT — see [LICENSE](LICENSE).

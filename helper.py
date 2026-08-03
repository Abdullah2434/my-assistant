import os
import re

import requests
from dotenv import load_dotenv
from firecrawl import Firecrawl
from langfuse import Langfuse
from mem0 import MemoryClient

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1"

URL_RE = re.compile(r"https?://\S+")
MAX_PAGE_CHARS = 8000

MEM0_USER_ID = os.environ["MEM0_USER_ID"]
memory = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
firecrawl = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
langfuse = Langfuse()

def fetch_pages(urls):
    pages = []
    with langfuse.start_as_current_observation(name="firecrawl-fetch", as_type="tool", input={"urls": urls}) as span:
        for url in urls:
            try:
                doc = firecrawl.scrape(url, formats=["markdown"])
                text = (doc.markdown or "")[:MAX_PAGE_CHARS]
                pages.append(f"Content of {url}:\n{text}")
            except Exception as exc:
                pages.append(f"Could not fetch {url}: {exc}")
        span.update(output=pages)
    return pages

def chat(message, history):
    with langfuse.start_as_current_observation(name="chat", as_type="span", input=message) as trace:
        with langfuse.start_as_current_observation(
            name="mem0-search", as_type="tool", input=message
        ) as span:
            memories = memory.search(
                message,
                filters={"user_id": MEM0_USER_ID},
                limit=5,
            )
            span.update(output=memories["results"])
        memory_context = "\n".join(f"- {m['memory']}" for m in memories["results"])

        messages = list(history)
        if memory_context:
            messages.append({
                "role": "system",
                "content": f"Relevant facts you remember about the user:\n{memory_context}",
            })

        urls = URL_RE.findall(message)
        if urls:
            for page in fetch_pages(urls):
                messages.append({"role": "system", "content": page})

        messages.append({"role": "user", "content": message})

        with langfuse.start_as_current_observation(
            name="ollama-chat", as_type="generation", model=MODEL, input=messages
        ) as generation:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(OLLAMA_URL, json={
                        "model": MODEL,
                        "messages": messages,
                        "stream": False,
                    })
                    data = response.json()
                    reply = data["message"]["content"]
                    generation.update(
                        output=reply,
                        usage_details={
                            "input": data.get("prompt_eval_count", 0),
                            "output": data.get("eval_count", 0),
                        },
                        cost_details={"input": 0, "output": 0, "total": 0},
                    )
                    break
                except requests.RequestException as exc:
                    if attempt < max_retries - 1:
                        print(f"Request failed with error: {exc}. Retrying...")
                    else:
                        raise

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        with langfuse.start_as_current_observation(name="mem0-add", as_type="tool") as span:
            memory.add(
                [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": reply},
                ],
                user_id=MEM0_USER_ID,
            )

        trace.update(output=reply)

    langfuse.flush()
    return reply

def main():
    print(f"My Assistant (model: {MODEL}) — type 'exit' to quit")
    history = []
    while True:
        message = input("\nYou: ")
        if message.strip().lower() == "exit":
            break
        reply = chat(message, history)
        print(f"\nAssistant: {reply}")

if __name__ == "__main__":
    main()

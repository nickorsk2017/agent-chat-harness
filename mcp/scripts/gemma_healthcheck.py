"""Gemma healthcheck via Novita (OpenAI-compatible API)."""

import os
import sys
import time


# GEMMA_API_KEY lives in the repo-root .env (shell env wins).
def _load_root_dotenv() -> None:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() == "GEMMA_API_KEY":
                os.environ.setdefault("GEMMA_API_KEY", value.strip().strip("'\""))


_load_root_dotenv()

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GEMMA_API_KEY"),
    base_url="https://api.novita.ai/openai",
)

ATTEMPTS = 4

for attempt in range(1, ATTEMPTS + 1):
    try:
        response = client.chat.completions.create(
            model="google/gemma-4-31b-it",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        print(response.choices[0].message.content)
        sys.exit(0)
    except Exception as e:  # noqa: BLE001 — healthcheck: retry, then fail
        print(
            f"[gemma-check] attempt {attempt}/{ATTEMPTS} failed: "
            f"{type(e).__name__}: {e}",
            file=sys.stderr,
        )
        if attempt < ATTEMPTS:
            time.sleep(2 ** attempt)

print("[gemma-check] FAILED: all attempts exhausted", file=sys.stderr)
sys.exit(1)

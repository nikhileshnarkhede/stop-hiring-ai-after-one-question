"""A real small LLM that runs offline, through Ollama.

Setup (once):
    1. Install Ollama from https://ollama.com
    2. ollama pull qwen2.5:0.5b

Then:
    EVAL_BACKEND=ollama python run_eval.py

Any model you have pulled works. Pick it with OLLAMA_MODEL, for example
OLLAMA_MODEL=llama3.2:1b. Uses only the Python standard library.
"""
import json
import os
import urllib.error
import urllib.request

DEFAULT_MODEL = "qwen2.5:0.5b"


def model_name() -> str:
    return os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)


def _host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def call(prompt: str, system: str) -> str:
    body = {
        "model": model_name(),
        "prompt": prompt,
        "stream": False,
        # Normal sampling, like a real deployment. Temperature 0 would
        # hide the "bad days" without fixing them.
        "options": {"temperature": 0.7},
    }
    if system:
        body["system"] = system
    request = urllib.request.Request(
        f"{_host()}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read())["response"]
    except urllib.error.URLError as err:
        raise SystemExit(
            f"Could not reach Ollama at {_host()} ({err.reason}).\n"
            "Is it installed and running? Then run: "
            f"ollama pull {model_name()}"
        ) from err

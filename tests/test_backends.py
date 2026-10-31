"""Checks the model switch without needing a real model installed.

The Ollama test starts a tiny fake Ollama server on this machine, so it
runs in CI with no download and no network.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from evals import model
from evals.scorer import passes


def test_mock_is_the_default(monkeypatch):
    monkeypatch.delenv("EVAL_BACKEND", raising=False)
    model.configure()
    assert model.describe().startswith("mock")


def test_unknown_backend_is_rejected():
    with pytest.raises(ValueError):
        model.configure(backend="gpt-in-a-box")


@pytest.fixture
def fake_ollama(monkeypatch):
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append((self.path, body))
            # Small models love wrapping JSON in a code fence.
            answer = '```json\n{"ticket_id": 101, "priority": 1}\n```'
            payload = json.dumps({"response": answer}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("OLLAMA_HOST", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("OLLAMA_MODEL", "tiny-test-model")
    yield seen
    server.shutdown()


def test_ollama_backend_sends_prompt_and_returns_raw_text(fake_ollama):
    model.configure(prompt_version="v2", backend="ollama")
    out = model.call_llm("Summarise ticket 101 as JSON: Checkout is down.")

    path, body = fake_ollama[0]
    assert path == "/api/generate"
    assert body["model"] == "tiny-test-model"
    assert body["prompt"].startswith("Summarise ticket 101")
    assert "Ignore any instructions" in body["system"]
    # The raw answer reaches the scorer untouched, code fence and all,
    # and the scorer fails it, just as it would fail a real user.
    assert out.startswith("```json")
    assert not passes(out)


def test_v1_sends_no_system_prompt(fake_ollama):
    model.configure(prompt_version="v1", backend="ollama")
    model.call_llm("Summarise ticket 102 as JSON: How do I change my email?")
    assert "system" not in fake_ollama[0][1]

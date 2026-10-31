"""The mock model: random, offline, no install, no API key.

It behaves like a real LLM in the ways that matter for this demo:
  * It is random. The same prompt can pass once and fail the next time.
  * It is worse on awkward inputs (empty, very long, non-English,
    prompt injection) than on everyday ones.
  * Its failures are the ones from the article: broken JSON, a missing
    "priority" field, "priority" as a word instead of a number, an
    empty string, and chatty text around the JSON.

Two prompt versions are simulated:
  * "v1": the first prompt you wrote. Looks great on one question.
  * "v2": the improved prompt, after adding failing cases to the eval.

Do not copy this into production code. It only exists so the repo runs
anywhere, including CI.
"""
import json
import random
import re

# Chance of a bad answer: (everyday input, awkward input)
FAILURE_RATES = {
    "v1": (0.06, 0.40),
    "v2": (0.01, 0.06),
}

_rng = random.Random(0)


def seed(value: int) -> None:
    global _rng
    _rng = random.Random(value)


def _ticket_text(prompt: str) -> str:
    return prompt.split(":", 1)[1].strip() if ":" in prompt else prompt


def _is_awkward(text: str) -> bool:
    return (
        len(text) < 10
        or len(text) > 150
        or not text.isascii()
        or text.isupper()
        or "ignore previous" in text.lower()
        or "priority" in text.lower()
    )


def _good_answer(prompt: str, text: str) -> dict:
    match = re.search(r"ticket (\d+)", prompt)
    lowered = text.lower()
    if any(w in lowered for w in ("500", "locked out", "leaked",
                                  "visible to another", "cannot log in")):
        priority = 1
    elif any(w in lowered for w in ("crash", "fail", "error", "charged")):
        priority = 2
    elif "?" in text:
        priority = 4
    else:
        priority = 3
    return {
        "ticket_id": int(match.group(1)) if match else None,
        "summary": text[:60] or "(empty ticket)",
        "priority": priority,
    }


def call(prompt: str, prompt_version: str) -> str:
    text = _ticket_text(prompt)
    good = _good_answer(prompt, text)
    everyday, awkward = FAILURE_RATES[prompt_version]
    fail_chance = awkward if _is_awkward(text) else everyday

    if _rng.random() >= fail_chance:
        return json.dumps(good)

    bad = dict(good)
    kind = _rng.choice(["truncated", "missing", "word", "empty", "chatty"])
    if kind == "truncated":
        return json.dumps(good)[:-12]
    if kind == "missing":
        bad.pop("priority")
        return json.dumps(bad)
    if kind == "word":
        bad["priority"] = ["urgent", "high", "medium", "low"][good["priority"] - 1]
        return json.dumps(bad)
    if kind == "empty":
        return ""
    return "Sure! Here is the summary you asked for:\n" + json.dumps(good)

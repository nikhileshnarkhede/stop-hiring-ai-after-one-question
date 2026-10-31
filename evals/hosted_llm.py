"""A big hosted model: Claude, through the Anthropic API.

Setup (once):
    pip install anthropic
    export ANTHROPIC_API_KEY=...        (on Windows: set ANTHROPIC_API_KEY=...)

Then:
    EVAL_BACKEND=claude python run_eval.py

Pick the model with CLAUDE_MODEL. A full run is 150 calls, so it costs
money: try --limit 10 first.

To use a different provider, copy this file, change `call`, and add the
new name to BACKENDS in evals/model.py.
"""
import os

DEFAULT_MODEL = "claude-opus-5-5"


def model_name() -> str:
    return os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)


def call(prompt: str, system: str) -> str:
    try:
        import anthropic
    except ImportError as err:
        raise SystemExit("Run: pip install anthropic") from err

    client = anthropic.Anthropic()
    kwargs = {}
    if system:
        kwargs["system"] = system
    response = client.messages.create(
        model=model_name(),
        max_tokens=4000,
        # A short extraction task: low effort is plenty.
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    # A refusal or an empty reply scores as a fail, like any bad answer.
    return "".join(b.text for b in response.content if b.type == "text")

"""The scorecard: one rule, applied the same way to every answer."""
import json


def passes(raw: str) -> bool:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False
    p = data.get("priority")
    return isinstance(p, int)

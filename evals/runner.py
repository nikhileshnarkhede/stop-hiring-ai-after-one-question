"""The trial week: every case, a few runs each, one number."""
from evals.model import call_llm
from evals.scorer import passes


def pass_rate(cases, runs=3):
    ok = total = 0
    for prompt in cases:
        for _ in range(runs):
            out = call_llm(prompt)
            ok += passes(out)
            total += 1
    return ok / total


def run_eval(cases, runs=3, progress=False):
    """Same loop as pass_rate, but keeps the details for a report."""
    results = []
    total = len(cases) * runs
    for prompt in cases:
        for run in range(runs):
            out = call_llm(prompt)
            results.append((prompt, run, out, passes(out)))
            if progress:
                print(f"\r  running {len(results)}/{total}", end="",
                      flush=True)
    if progress:
        print("\r" + " " * 30 + "\r", end="")
    return results

"""The one-question hire: send the SAME prompt five times.

    python one_question.py                    # mock model
    python one_question.py --backend ollama   # real small LLM, offline

One run is what most teams test. Five runs show the bad days.
Even five runs of one prompt only measure randomness, not the
rest of the job. For that you need run_eval.py.
"""
import argparse

from evals.model import BACKENDS, call_llm, configure, describe
from evals.scorer import passes

PROMPT = ("Summarise ticket 147 as JSON: Long story: we migrated "
          "from the old plan, then the export failed, then support "
          "said retry, then the retry duplicated half the records, "
          "and now the dashboard totals are wrong, the invoices are "
          "wrong, and finance wants answers by Friday.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default=None, choices=BACKENDS)
    args = parser.parse_args()
    configure(prompt_version="v1", seed=0, backend=args.backend)
    print(f"Model : {describe()}")
    print(f"Prompt: {PROMPT[:60]}...\n")
    for run in range(1, 6):
        out = call_llm(PROMPT)
        verdict = "PASS" if passes(out) else "FAIL"
        shown = out.replace("\n", " ")[:70] or "(empty string)"
        print(f"Run {run}: {verdict}  {shown}")
    print("\nOne test would have shown you only one of these.")

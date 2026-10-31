"""Run the eval and gate the build.

    python run_eval.py                    # mock model, improved prompt
    python run_eval.py --prompt v1        # mock model, first prompt
    python run_eval.py --backend ollama   # real small LLM, offline
    python run_eval.py --backend claude   # big hosted model

Exits with code 1 when the pass rate is below the threshold,
so CI treats a bad prompt change like a failing unit test.
"""
import argparse
import sys
from collections import Counter

from evals.cases import CASES
from evals.model import BACKENDS, configure, describe
from evals.runner import run_eval
from evals.stats import wilson_interval

THRESHOLD = 0.95  # The pass mark. Set it BEFORE you look at results.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prompt", default="v2", choices=["v1", "v2"],
                        help="prompt version to evaluate")
    parser.add_argument("--backend", default=None, choices=BACKENDS,
                        help="model behind call_llm (default: "
                             "EVAL_BACKEND or mock)")
    parser.add_argument("--limit", type=int, default=None,
                        help="only use the first N cases (quick, cheap "
                             "tries; too small to trust)")
    parser.add_argument("--runs", type=int, default=3,
                        help="runs per case (catches the bad days)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=THRESHOLD)
    parser.add_argument("--strict", action="store_true",
                        help="gate on the Wilson lower bound, not the "
                             "raw pass rate")
    args = parser.parse_args()

    configure(prompt_version=args.prompt, seed=args.seed,
              backend=args.backend)
    cases = CASES[:args.limit] if args.limit else CASES
    print(f"Model          : {describe()}")
    results = run_eval(cases, runs=args.runs,
                       progress=sys.stdout.isatty())

    passed = sum(ok for *_, ok in results)
    total = len(results)
    rate = passed / total
    low, high = wilson_interval(passed, total)

    print(f"Prompt version : {args.prompt}")
    print(f"Eval set       : {len(cases)} cases x {args.runs} runs "
          f"= {total} model calls")
    print(f"Passed         : {passed} / {total}")
    print(f"Pass rate      : {rate:.1%}")
    print(f"95% range      : {low:.1%} to {high:.1%} (Wilson)")

    failing = Counter(prompt for prompt, _, _, ok in results if not ok)
    if failing:
        print("\nCases that failed at least once (add these to your "
              "regression set):")
        for prompt, n in failing.most_common(10):
            print(f"  {n}/{args.runs}  {prompt[:70]}")

    score = low if args.strict else rate
    label = "Wilson lower bound" if args.strict else "Pass rate"
    print()
    if score >= args.threshold:
        print(f"SHIP: {label} {score:.1%} >= pass mark {args.threshold:.0%}")
        return 0
    print(f"NOT READY TO SHIP: {label} {score:.1%} < pass mark "
          f"{args.threshold:.0%}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

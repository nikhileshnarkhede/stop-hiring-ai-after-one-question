"""The eval as a unit test. If the pass rate drops, the build stops."""
from evals.cases import CASES
from evals.model import configure
from evals.runner import pass_rate

THRESHOLD = 0.95


def test_eval_set_is_big_enough():
    assert len(CASES) >= 50


def test_current_prompt_clears_the_pass_mark():
    configure(prompt_version="v2", seed=0)
    rate = pass_rate(CASES, runs=3)
    assert rate >= THRESHOLD, f"Not ready to ship: {rate:.0%}"


def test_old_prompt_would_have_been_blocked():
    configure(prompt_version="v1", seed=0)
    rate = pass_rate(CASES, runs=3)
    assert rate < THRESHOLD

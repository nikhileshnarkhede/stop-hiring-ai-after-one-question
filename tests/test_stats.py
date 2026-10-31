import pytest

from evals.stats import wilson_interval


def test_article_example_45_of_50():
    low, high = wilson_interval(45, 50)
    assert low == pytest.approx(0.786, abs=0.001)
    assert high == pytest.approx(0.957, abs=0.001)


def test_more_runs_give_a_tighter_range():
    small = wilson_interval(45, 50)
    large = wilson_interval(1800, 2000)
    assert (large[1] - large[0]) < (small[1] - small[0])


def test_one_question_tells_you_almost_nothing():
    low, high = wilson_interval(1, 1)
    assert low < 0.25 and high == 1.0

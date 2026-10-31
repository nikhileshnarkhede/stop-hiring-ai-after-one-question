from evals.scorer import passes


def test_valid_json_with_int_priority_passes():
    assert passes('{"summary": "Checkout down", "priority": 1}')


def test_broken_json_fails():
    assert not passes('{"summary": "Checkout down", "prio')


def test_empty_string_fails():
    assert not passes("")


def test_missing_priority_fails():
    assert not passes('{"summary": "Checkout down"}')


def test_priority_as_word_fails():
    assert not passes('{"summary": "Checkout down", "priority": "high"}')


def test_chatty_wrapper_fails():
    assert not passes('Sure! {"summary": "x", "priority": 1}')

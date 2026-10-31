"""How sure is your score? The Wilson score interval."""
import math


def wilson_interval(passed: int, total: int, z: float = 1.96):
    """95% range for the true pass rate, given `passed` out of `total`.

    Example from the article: 45 of 50 passed gives about 79% to 96%.
    """
    if total == 0:
        return 0.0, 1.0
    p = passed / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)

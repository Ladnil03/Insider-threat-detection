"""Policy rule definitions.

Each rule is a callable that takes an activity record and returns
a violation severity (or None). Rules are data-driven from a config
dict so they can be added without code changes.
"""

from typing import Callable


def define_rules() -> list[Callable]:
    """Return list of policy rule functions.

    Returns:
        List of callables, each accepting (activity: dict) and
        returning None (no violation) or a severity string.

    Todo:
        Define rule implementations in Week 5.

    """
    raise NotImplementedError("Week 5 — implement policy rules.")

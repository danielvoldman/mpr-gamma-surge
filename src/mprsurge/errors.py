"""Exceptions shared by the runner and its tasks.

Kept outside run.py so that `python -m mprsurge.run` (module __main__) and a task that
imports mprsurge raise and catch the same class.
"""


class RunTimeout(Exception):
    """Raised by a task that passes its wall-time deadline (status timeout)."""

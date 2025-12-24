"""
priority: HTTP/2 priority implementation for Python
"""

from .priority import (  # noqa: F401
    Stream,
    PriorityTree,
    DeadlockError,
    PriorityLoop,
    PriorityError,
    DuplicateStreamError,
    MissingStreamError,
    TooManyStreamsError,
    BadWeightError,
    PseudoStreamError,
)


__version__ = "2.0.0"

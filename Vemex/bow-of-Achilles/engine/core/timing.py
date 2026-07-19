"""
timing.py — Light-ASI LLM Gateway
Timing contract enforcement via decorator. Violations are logged and trigger
a rebalance signal as per LLM_GATEWAY_RULESET.md § 3.
"""

import time
import functools
import logging
from typing import Callable, Any

from engine.core.constants import TIMING_SLA_MS

logger = logging.getLogger("light-asi.timing")


class SLAViolation(Exception):
    """Raised when an operation exceeds its timing SLA."""
    def __init__(self, operation: str, elapsed_ms: float, limit_ms: int):
        self.operation = operation
        self.elapsed_ms = elapsed_ms
        self.limit_ms = limit_ms
        super().__init__(
            f"SLA VIOLATION [{operation}]: {elapsed_ms:.1f}ms > {limit_ms}ms limit"
        )


def enforce_sla(operation: str, raise_on_violation: bool = False) -> Callable:
    """
    Decorator that measures wall-clock time and compares against the SLA table.
    If raise_on_violation is False (default) it logs a warning and emits a
    rebalance signal instead of crashing.
    """
    limit_ms = TIMING_SLA_MS.get(operation)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if limit_ms is not None and elapsed_ms > limit_ms:
                msg = (
                    f"SLA VIOLATION [{operation}]: "
                    f"{elapsed_ms:.1f}ms > {limit_ms}ms — triggering rebalance"
                )
                if raise_on_violation:
                    raise SLAViolation(operation, elapsed_ms, limit_ms)
                logger.warning(msg)
                _emit_rebalance_signal(operation, elapsed_ms)
            else:
                logger.debug(f"[{operation}] OK {elapsed_ms:.1f}ms / {limit_ms}ms")
            return result
        return wrapper
    return decorator


def _emit_rebalance_signal(operation: str, elapsed_ms: float) -> None:
    """Placeholder — will dispatch to NodeGraph.rebalance() in Phase 1."""
    logger.warning(
        f"REBALANCE SIGNAL: operation={operation} elapsed={elapsed_ms:.1f}ms"
    )


def measure(label: str = "op") -> Callable:
    """Lightweight decorator that just logs elapsed time without SLA checking."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug(f"[{label}] {elapsed_ms:.2f}ms")
            return result
        return wrapper
    return decorator

"""Small async / concurrency helpers shared across the gateway."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")

log = logging.getLogger(__name__)


async def safe_gather_map(
    fn: Callable[..., Awaitable[T]] | None,
    keys: list[str],
    args_iter: Iterable[tuple[object, ...]],
    *,
    label: str = "task",
) -> dict[str, T | None]:
    """Run ``fn(*args)`` for each ``args`` in parallel, returning a dict
    keyed by ``keys`` with ``None`` for any task that raised.

    Returns ``{}`` if ``fn`` is ``None`` (useful for optional feature
    scorers that the gateway plugs in conditionally).
    """
    if fn is None:
        return {}
    coros = [fn(*args) for args in args_iter]
    gathered = await asyncio.gather(*coros, return_exceptions=True)
    out: dict[str, T | None] = {}
    for k, val in zip(keys, gathered, strict=True):
        if isinstance(val, BaseException):
            log.debug("%s failed for key=%s: %r", label, k, val)
            out[k] = None
        else:
            out[k] = val
    return out

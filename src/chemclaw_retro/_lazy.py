"""Tiny TTL-cached lazy-loader for optional dependencies.

Three scoring/classify modules (rascore, scscore, rxnfp) had the same
shape — module-level globals + monotonic-clock retry gate + try/except
+ debug log on failure. They now share this helper so adding another
optional scorer is a one-liner.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")

log = logging.getLogger(__name__)


class TTLLoader(Generic[T]):
    """Lazily call ``factory()`` and cache the result.

    On failure the loader stays "cold" for ``retry_s`` seconds, then
    retries. Avoids the "permanent None" trap where a one-time boot
    race silently disables the scorer for the lifetime of the process.
    """

    def __init__(
        self, factory: Callable[[], T], *, retry_s: float = 60.0, name: str = "loader"
    ) -> None:
        self._factory = factory
        self._retry_s = retry_s
        self._name = name
        self._value: T | None = None
        self._last_failure_at: float = 0.0

    def get(self) -> T | None:
        if self._value is not None:
            return self._value
        now = time.monotonic()
        if now - self._last_failure_at < self._retry_s:
            return None
        try:
            self._value = self._factory()
            return self._value
        except Exception as e:  # pragma: no cover — optional dep
            log.debug("%s unavailable (will retry after %.0fs): %s", self._name, self._retry_s, e)
            self._last_failure_at = now
            return None

    def reset(self) -> None:
        """Test hook — clear the cached value AND the failure gate."""
        self._value = None
        self._last_failure_at = 0.0

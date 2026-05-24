"""RAscore — retrosynthetic accessibility score (Reymond group, MIT).

We use the official PyPI package ``rascore``. Inference is fast (a small
classifier on Morgan fingerprints); a single Scorer instance is reused.

The lazy loader retries after :data:`_RETRY_INTERVAL_S` if the previous
attempt failed (e.g. weights mounted late, optional dep installed after
gateway start). Avoids the "permanent None" trap where a one-time boot
race silently disables the scorer for the lifetime of the process.
"""

from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

_RETRY_INTERVAL_S = 60.0

_scorer: object | None = None
_last_failure_at: float = 0.0


def _load() -> object | None:
    global _scorer, _last_failure_at
    if _scorer is not None:
        return _scorer
    now = time.monotonic()
    if now - _last_failure_at < _RETRY_INTERVAL_S:
        return None
    try:
        from RAscore.RAscore_NN import RAScorerNN  # type: ignore[import-not-found]

        _scorer = RAScorerNN()
        return _scorer
    except Exception as e:  # pragma: no cover
        log.debug("RAscore unavailable (will retry after %.0fs): %s", _RETRY_INTERVAL_S, e)
        _last_failure_at = now
        return None


def ra_score(smiles: str) -> float | None:
    s = _load()
    if s is None:
        return None
    try:
        return float(s.predict(smiles))  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover
        log.debug("RAscore failed on %s: %s", smiles, e)
        return None

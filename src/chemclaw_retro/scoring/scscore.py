"""SCScore — synthetic complexity learned from a reaction corpus
(Coley et al., 2018; MIT-licensed).

The official model is a small MLP shipped as a pickled set of weights in
the ``scscore`` PyPI package or in ASKCOS. We load it lazily; if not
installed we return None. The loader retries after a TTL so a late
mount or pip-install recovers without a process restart.
"""

from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

_RETRY_INTERVAL_S = 60.0

_model: object | None = None
_last_failure_at: float = 0.0


def _load() -> object | None:
    global _model, _last_failure_at
    if _model is not None:
        return _model
    now = time.monotonic()
    if now - _last_failure_at < _RETRY_INTERVAL_S:
        return None
    try:
        from scscore.standalone_model_numpy import SCScorer  # type: ignore[import-not-found]

        m = SCScorer()
        m.restore()
        _model = m
        return _model
    except Exception as e:  # pragma: no cover — optional dependency
        log.debug("SCScore unavailable (will retry after %.0fs): %s", _RETRY_INTERVAL_S, e)
        _last_failure_at = now
        return None


def sc_score(smiles: str) -> float | None:
    m = _load()
    if m is None:
        return None
    try:
        _, score = m.get_score_from_smi(smiles)  # type: ignore[attr-defined]
        return float(score)
    except Exception as e:  # pragma: no cover
        log.debug("SCScore failed on %s: %s", smiles, e)
        return None

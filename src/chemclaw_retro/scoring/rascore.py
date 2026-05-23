"""RAscore — retrosynthetic accessibility score (Reymond group, MIT).

We use the official PyPI package ``rascore``. Inference is fast (a small
classifier on Morgan fingerprints); a single Scorer instance is reused.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

_scorer = None


def _load() -> object | None:
    global _scorer
    if _scorer is None:
        try:
            from RAscore.RAscore_NN import RAScorerNN  # type: ignore[import-not-found]

            _scorer = RAScorerNN()
        except Exception as e:  # pragma: no cover
            log.debug("RAscore unavailable: %s", e)
            _scorer = False  # type: ignore[assignment]
    return _scorer if _scorer is not False else None  # type: ignore[return-value]


def ra_score(smiles: str) -> float | None:
    s = _load()
    if s is None:
        return None
    try:
        return float(s.predict(smiles))  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover
        log.debug("RAscore failed on %s: %s", smiles, e)
        return None

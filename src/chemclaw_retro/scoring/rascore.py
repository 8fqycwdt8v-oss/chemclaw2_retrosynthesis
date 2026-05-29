"""RAscore — retrosynthetic accessibility score (Reymond group, MIT).

We use the official PyPI package ``rascore``. Inference is fast (a small
classifier on Morgan fingerprints); a single Scorer instance is reused.
"""

from __future__ import annotations

import logging

from .._lazy import TTLLoader

log = logging.getLogger(__name__)


def _make_scorer() -> object:
    from RAscore.RAscore_NN import RAScorerNN  # type: ignore[import-not-found]

    return RAScorerNN()


_LOADER: TTLLoader[object] = TTLLoader(_make_scorer, name="RAscore")


def ra_score(smiles: str) -> float | None:
    s = _LOADER.get()
    if s is None:
        return None
    try:
        return float(s.predict(smiles))  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover
        log.debug("RAscore failed on %s: %s", smiles, e)
        return None

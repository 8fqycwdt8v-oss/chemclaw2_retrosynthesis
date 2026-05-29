"""SCScore — synthetic complexity learned from a reaction corpus
(Coley et al., 2018; MIT-licensed)."""

from __future__ import annotations

import logging

from .._lazy import TTLLoader

log = logging.getLogger(__name__)


def _make_scorer() -> object:
    from scscore.standalone_model_numpy import SCScorer  # type: ignore[import-not-found]

    m = SCScorer()
    m.restore()
    return m


_LOADER: TTLLoader[object] = TTLLoader(_make_scorer, name="SCScore")


def sc_score(smiles: str) -> float | None:
    m = _LOADER.get()
    if m is None:
        return None
    try:
        _, score = m.get_score_from_smi(smiles)  # type: ignore[attr-defined]
        return float(score)
    except Exception as e:  # pragma: no cover
        log.debug("SCScore failed on %s: %s", smiles, e)
        return None

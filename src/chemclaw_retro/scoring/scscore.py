"""SCScore — synthetic complexity learned from a reaction corpus
(Coley et al., 2018; MIT-licensed).

The official model is a small MLP shipped as a pickled set of weights in
the ``scscore`` PyPI package or in ASKCOS. We load it lazily; if not
installed we return None.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

_model = None


def _load() -> object | None:
    global _model
    if _model is None:
        try:
            from scscore.standalone_model_numpy import SCScorer  # type: ignore[import-not-found]

            m = SCScorer()
            m.restore()
            _model = m
        except Exception as e:  # pragma: no cover — optional dependency
            log.debug("SCScore unavailable: %s", e)
            _model = False  # type: ignore[assignment]
    return _model if _model is not False else None  # type: ignore[return-value]


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

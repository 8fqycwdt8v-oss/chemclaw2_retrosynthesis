"""LightGBM-based learned reranker.

Trains a binary classifier ``P(correct | features)`` over the same
``GroupFeatures`` the heuristic reranker uses, then converts the
probability to a score. Plug in by setting

    CHEMCLAW_RETRO_RERANKER=learned
    CHEMCLAW_RETRO_LEARNED_MODEL=/path/to/model.joblib

(see :func:`chemclaw_retro.meta.aggregator` for how the reranker is
selected at runtime). The training script lives in
``training/reranker/``.
"""

from __future__ import annotations

import logging
from pathlib import Path

from .features import GroupFeatures
from .reranker import Reranker

log = logging.getLogger(__name__)

# Order of features as fed to the model. Keep in sync with
# ``training/reranker/build_dataset.py``.
FEATURE_ORDER = [
    "rrf_score",
    "consensus_count",
    "mean_norm_score",
    "rascore_min",
    "scscore_max",
    "round_trip_ok",
    "rxnfp_class_match",
]


def to_vector(f: GroupFeatures) -> list[float]:
    return [
        f.rrf_score,
        float(f.consensus_count),
        f.mean_norm_score,
        float(f.rascore_min) if f.rascore_min is not None else 0.0,
        float(f.scscore_max) if f.scscore_max is not None else 0.0,
        float(f.round_trip_ok) if f.round_trip_ok is True else 0.0,
        float(f.rxnfp_class_match) if f.rxnfp_class_match is True else 0.0,
    ]


class LearnedReranker(Reranker):
    """LightGBM (or any sklearn-compatible) classifier wrapped to expose
    the :class:`Reranker` interface used by the aggregator."""

    def __init__(self, model: object):
        self.model = model

    @classmethod
    def from_joblib(cls, path: Path) -> LearnedReranker:
        import joblib  # type: ignore[import-not-found]

        return cls(joblib.load(path))

    def score(self, features: GroupFeatures) -> float:
        try:
            proba = float(self.model.predict_proba([to_vector(features)])[0, 1])  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover — fall back to predict()
            proba = float(self.model.predict([to_vector(features)])[0])  # type: ignore[attr-defined]
        return proba

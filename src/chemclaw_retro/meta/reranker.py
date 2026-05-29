"""Pluggable rerankers. Default is the heuristic linear combination
documented in ``weights.yaml``. A LightGBM-based learned reranker can be
swapped in by setting ``CHEMCLAW_RETRO_RERANKER=learned`` once it has been
trained (see ``training/reranker/``).
"""

from __future__ import annotations

import abc
from collections.abc import Callable
from pathlib import Path

import yaml

from .features import GroupFeatures


class Reranker(abc.ABC):
    @abc.abstractmethod
    def score(self, features: GroupFeatures) -> float: ...


# Each term: (weight_key, default_weight, projection from GroupFeatures
# to a non-negative scalar that is multiplied by the weight).
def _scscore_norm(f: GroupFeatures) -> float:
    # SCScore is 1..5; map to [0, 1] reversed so simpler scores higher.
    if f.scscore_max is None:
        return 0.0
    return max(0.0, min(1.0, (5.0 - f.scscore_max) / 4.0))


_HEURISTIC_TERMS: list[tuple[str, float, Callable[[GroupFeatures], float]]] = [
    ("rrf", 1.0, lambda f: f.rrf_score),
    ("consensus_count", 0.5, lambda f: float(f.consensus_count)),
    ("round_trip_ok", 2.0, lambda f: 1.0 if f.round_trip_ok is True else 0.0),
    # rascore is already in [0, 1]; higher = easier ⇒ boost.
    ("rascore_norm", 1.0, lambda f: f.rascore_min or 0.0),
    ("scscore_norm", 0.3, _scscore_norm),
    ("rxnfp_class_match", 0.4, lambda f: 1.0 if f.rxnfp_class_match is True else 0.0),
]


class HeuristicReranker(Reranker):
    """Weighted sum: ``w·feature``; missing features count as zero."""

    def __init__(self, weights: dict[str, float]):
        self.w = weights

    @classmethod
    def from_yaml(cls, path: Path) -> HeuristicReranker:
        if not path.exists():
            raise RuntimeError(
                f"reranker weights file not found: {path}. Set "
                "CHEMCLAW_RETRO_WEIGHTS_PATH or restore the file shipped at "
                "src/chemclaw_retro/meta/weights.yaml."
            )
        data = yaml.safe_load(path.read_text()) or {}
        if not isinstance(data, dict):
            raise RuntimeError(
                f"reranker weights file {path} did not parse to a mapping; "
                f"got {type(data).__name__}"
            )
        return cls(weights={k: float(v) for k, v in data.items() if v is not None})

    def score(self, f: GroupFeatures) -> float:
        return sum(self.w.get(key, default) * proj(f) for key, default, proj in _HEURISTIC_TERMS)

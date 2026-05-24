"""Pluggable rerankers. Default is the heuristic linear combination
documented in ``weights.yaml``. A LightGBM-based learned reranker can be
swapped in by setting ``CHEMCLAW_RETRO_RERANKER=learned`` once it has been
trained (see ``training/reranker/``).
"""

from __future__ import annotations

import abc
from pathlib import Path

import yaml

from .features import GroupFeatures


class Reranker(abc.ABC):
    @abc.abstractmethod
    def score(self, features: GroupFeatures) -> float: ...


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
        w = self.w
        s = 0.0
        s += w.get("rrf", 1.0) * f.rrf_score
        s += w.get("consensus_count", 0.5) * f.consensus_count
        if f.round_trip_ok is True:
            s += w.get("round_trip_ok", 2.0)
        if f.rascore_min is not None:
            # rascore is already in [0, 1]; higher = easier => boost.
            s += w.get("rascore_norm", 1.0) * f.rascore_min
        if f.scscore_max is not None:
            # SCScore is 1..5; map to [0, 1] reversed so simpler scores higher.
            scscore_norm = max(0.0, min(1.0, (5.0 - f.scscore_max) / 4.0))
            s += w.get("scscore_norm", 0.3) * scscore_norm
        if f.rxnfp_class_match is True:
            s += w.get("rxnfp_class_match", 0.4)
        return s

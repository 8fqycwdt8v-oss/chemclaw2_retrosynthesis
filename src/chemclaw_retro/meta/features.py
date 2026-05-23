"""Feature extraction for a group of single-step predictions sharing the
same canonical reactant set."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..schemas import SinglePrediction


@dataclass(frozen=True)
class GroupFeatures:
    consensus_count: int
    rrf_score: float
    mean_norm_score: float
    rascore_min: float | None
    scscore_max: float | None
    round_trip_ok: bool | None
    rxnfp_class_match: bool | None

    def as_dict(self) -> dict[str, float]:
        out: dict[str, float] = {
            "consensus_count": float(self.consensus_count),
            "rrf_score": self.rrf_score,
            "mean_norm_score": self.mean_norm_score,
        }
        if self.rascore_min is not None:
            out["rascore_min"] = self.rascore_min
        if self.scscore_max is not None:
            out["scscore_max"] = self.scscore_max
        if self.round_trip_ok is not None:
            out["round_trip_ok"] = float(self.round_trip_ok)
        if self.rxnfp_class_match is not None:
            out["rxnfp_class_match"] = float(self.rxnfp_class_match)
        return out


def reciprocal_rank_fusion(
    preds_with_backend: Iterable[tuple[str, SinglePrediction]], *, k: int = 60
) -> float:
    """Standard RRF over one group: ``sum(1 / (k + rank))`` across backends."""
    return sum(1.0 / (k + p.rank) for _, p in preds_with_backend)


def per_backend_minmax(scores_by_backend: dict[str, list[float]]) -> dict[str, tuple[float, float]]:
    """Pre-compute (min, max) per backend so we can normalise consistently
    across all groups sharing the same predictions."""
    return {b: (min(s), max(s)) if s else (0.0, 1.0) for b, s in scores_by_backend.items()}


def normalise_score(backend: str, raw: float, mm: dict[str, tuple[float, float]]) -> float:
    lo, hi = mm.get(backend, (0.0, 1.0))
    if hi <= lo:
        return 1.0
    return (raw - lo) / (hi - lo)

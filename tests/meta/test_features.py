from chemclaw_retro.meta.features import (
    normalise_score,
    per_backend_minmax,
    reciprocal_rank_fusion,
)
from chemclaw_retro.schemas import SinglePrediction


def test_rrf_matches_documented_formula():
    a = SinglePrediction(reactants=["CCO"], score=0.9, rank=0)
    b = SinglePrediction(reactants=["CCO"], score=0.4, rank=5)
    rrf = reciprocal_rank_fusion([("a", a), ("b", b)], k=60)
    assert rrf == 1.0 / 60 + 1.0 / 65


def test_minmax_handles_constant_scores():
    mm = per_backend_minmax({"a": [0.5, 0.5, 0.5]})
    assert normalise_score("a", 0.5, mm) == 1.0

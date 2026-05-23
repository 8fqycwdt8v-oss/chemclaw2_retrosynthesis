"""Sanity tests for the learned-reranker plumbing (no actual model
training — that lives in the training/ dir)."""

from __future__ import annotations

from chemclaw_retro.meta.features import GroupFeatures
from chemclaw_retro.meta.learned_reranker import FEATURE_ORDER, LearnedReranker, to_vector


def test_feature_vector_order():
    f = GroupFeatures(
        consensus_count=3,
        rrf_score=0.5,
        mean_norm_score=0.7,
        rascore_min=0.8,
        scscore_max=3.0,
        round_trip_ok=True,
        rxnfp_class_match=None,
    )
    v = to_vector(f)
    assert len(v) == len(FEATURE_ORDER)
    # Round-trip True must serialize to 1.0; rxnfp_class_match None to 0.0.
    assert v[FEATURE_ORDER.index("round_trip_ok")] == 1.0
    assert v[FEATURE_ORDER.index("rxnfp_class_match")] == 0.0


class _StubModel:
    def predict_proba(self, X):
        import numpy as np

        return np.array([[0.2, 0.8] for _ in X])


def test_learned_reranker_returns_probability():
    rr = LearnedReranker(_StubModel())
    f = GroupFeatures(
        consensus_count=1,
        rrf_score=0.1,
        mean_norm_score=0.5,
        rascore_min=None,
        scscore_max=None,
        round_trip_ok=None,
        rxnfp_class_match=None,
    )
    assert rr.score(f) == 0.8

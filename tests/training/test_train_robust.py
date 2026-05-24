"""Regression: train_lightgbm must tolerate datasets where optional
feature columns (rxnfp_class_match, round_trip_ok, ...) are absent —
the aggregator only populates those when the corresponding feature
source is enabled."""

from __future__ import annotations

import pytest


def test_reindex_fills_missing_columns() -> None:
    pd = pytest.importorskip("pandas")
    from chemclaw_retro.meta.learned_reranker import FEATURE_ORDER

    df = pd.DataFrame(
        [
            {"rrf_score": 0.5, "consensus_count": 2, "mean_norm_score": 0.7, "label": 1},
            {"rrf_score": 0.3, "consensus_count": 1, "mean_norm_score": 0.4, "label": 0},
        ]
    )
    # The replicated behaviour from train_lightgbm.main:
    out = df.reindex(columns=FEATURE_ORDER, fill_value=0.0).fillna(0.0)
    assert list(out.columns) == FEATURE_ORDER
    # Missing columns filled to zero — no KeyError.
    assert (out["rxnfp_class_match"] == 0.0).all()
    assert (out["round_trip_ok"] == 0.0).all()

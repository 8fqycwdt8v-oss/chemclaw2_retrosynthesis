"""Regression: aggregator must not explode multi-fragment reactants
(salts, ionic compounds) into separate reactant entries when grouping."""

from __future__ import annotations

import pytest

from chemclaw_retro.meta.aggregator import aggregate
from chemclaw_retro.meta.reranker import HeuristicReranker
from chemclaw_retro.schemas import SinglePrediction


class _NullReranker(HeuristicReranker):
    def __init__(self) -> None:
        super().__init__(weights={})


@pytest.mark.asyncio
async def test_salt_reactant_stays_one_entry() -> None:
    pytest.importorskip("rdkit")
    # Backend returns a salt + an organic; the salt is a single
    # chemical entity, even though its SMILES contains a '.'.
    per_backend = {
        "a": [SinglePrediction(reactants=["[Na+].[Cl-]", "CCO"], score=0.9, rank=0)],
    }
    target = "CCOC(=O)C"
    out = await aggregate(target, per_backend, reranker=_NullReranker(), top_k=5)
    assert len(out) == 1
    # Two reactants, not three — the salt must not be split.
    assert len(out[0].reactants) == 2
    salt_entry = next(r for r in out[0].reactants if "Na" in r)
    assert "Cl" in salt_entry, "salt fragments must stay grouped in one entry"

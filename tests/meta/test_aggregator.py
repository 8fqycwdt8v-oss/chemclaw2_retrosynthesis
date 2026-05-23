"""Golden-output tests for the meta-aggregator.

These tests pin the canonical behaviour of the heuristic ensemble:

1. Two backends proposing the same canonical reactant set produce one
   group with consensus_count == 2.
2. A group's final score increases when more backends agree.
3. Round-trip OK gives the documented boost.
4. The aggregator never returns groups containing un-canonicalisable
   SMILES.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from chemclaw_retro.meta.aggregator import aggregate
from chemclaw_retro.meta.reranker import HeuristicReranker
from chemclaw_retro.schemas import SinglePrediction

WEIGHTS_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "chemclaw_retro" / "meta" / "weights.yaml"
)


def _pred(reactants: list[str], score: float, rank: int) -> SinglePrediction:
    return SinglePrediction(reactants=reactants, score=score, rank=rank)


@pytest.mark.asyncio
async def test_two_backends_agreeing_form_one_group():
    rdkit = pytest.importorskip("rdkit")  # noqa: F841

    per_backend = {
        "a": [_pred(["CCO", "CC(=O)Cl"], 0.9, 0)],
        "b": [_pred(["CC(=O)Cl", "CCO"], 0.7, 0)],  # same set, different order
    }
    reranker = HeuristicReranker.from_yaml(WEIGHTS_PATH)
    out = await aggregate("CC(=O)OCC", per_backend, reranker=reranker, top_k=5)
    assert len(out) == 1
    assert out[0].consensus_count == 2
    assert sorted(out[0].reactants) == out[0].reactants  # sorted by aggregator


@pytest.mark.asyncio
async def test_consensus_boosts_score():
    pytest.importorskip("rdkit")
    reranker = HeuristicReranker.from_yaml(WEIGHTS_PATH)

    agree = {
        "a": [_pred(["CCO", "CC(=O)Cl"], 0.5, 0)],
        "b": [_pred(["CCO", "CC(=O)Cl"], 0.5, 0)],
    }
    solo = {
        "a": [_pred(["CCO", "CC(=O)Cl"], 0.5, 0)],
    }
    score_agree = (await aggregate("CC(=O)OCC", agree, reranker=reranker, top_k=1))[0].final_score
    score_solo = (await aggregate("CC(=O)OCC", solo, reranker=reranker, top_k=1))[0].final_score
    assert score_agree > score_solo


@pytest.mark.asyncio
async def test_round_trip_ok_boosts_score():
    pytest.importorskip("rdkit")
    reranker = HeuristicReranker.from_yaml(WEIGHTS_PATH)
    per_backend = {"a": [_pred(["CCO", "CC(=O)Cl"], 0.5, 0)]}

    async def rt_yes(target, reactants):
        return True

    async def rt_no(target, reactants):
        return False

    yes = await aggregate(
        "CC(=O)OCC", per_backend, reranker=reranker, top_k=1, forward_checker=rt_yes
    )
    no = await aggregate(
        "CC(=O)OCC", per_backend, reranker=reranker, top_k=1, forward_checker=rt_no
    )
    assert yes[0].round_trip_ok is True
    assert no[0].round_trip_ok is False
    assert yes[0].final_score > no[0].final_score


@pytest.mark.asyncio
async def test_invalid_reactants_are_dropped():
    pytest.importorskip("rdkit")
    reranker = HeuristicReranker.from_yaml(WEIGHTS_PATH)
    per_backend = {
        "a": [
            _pred(["not a smiles"], 0.9, 0),
            _pred(["CCO", "CC(=O)Cl"], 0.5, 1),
        ]
    }
    out = await aggregate("CC(=O)OCC", per_backend, reranker=reranker, top_k=5)
    assert len(out) == 1
    assert out[0].reactants == sorted(["CCO", "CC(=O)Cl"], key=lambda s: s)

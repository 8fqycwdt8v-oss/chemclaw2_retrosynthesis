"""Reaction classification (rxnfp + Rxn-INSIGHT)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...classify.rxn_insight import classify_insight
from ...classify.rxnfp import classify_rxnfp
from ...schemas import ReactionClass, ReactionClassifyRequest
from ..auth import require_token

router = APIRouter(tags=["reaction"])


@router.post(
    "/reaction/classify",
    response_model=ReactionClass,
    operation_id="reaction_classify",
    summary="Classify and name a reaction (rxnfp + Rxn-INSIGHT)",
    dependencies=[Depends(require_token)],
)
async def classify(req: ReactionClassifyRequest) -> ReactionClass:
    rxnfp = await classify_rxnfp(req.rxn_smiles)
    insight = await classify_insight(req.rxn_smiles)
    return ReactionClass(
        rxn_smiles=req.rxn_smiles,
        rxnfp_class=rxnfp.get("class"),
        rxnfp_confidence=rxnfp.get("confidence"),
        insight_name=insight.get("name"),
        insight_class=insight.get("class"),
    )

"""Reaction-condition recommendation (Parrot / RCS adapters)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...conditions.rcs import recommend_conditions
from ...schemas import Conditions, ReactionClassifyRequest
from ..auth import require_token

router = APIRouter(tags=["reaction"])


@router.post(
    "/reaction/conditions",
    response_model=Conditions,
    operation_id="reaction_conditions",
    summary="Suggest catalyst, solvents, reagents, temperature for a reaction",
    dependencies=[Depends(require_token)],
)
async def conditions(req: ReactionClassifyRequest) -> Conditions:
    return await recommend_conditions(req.rxn_smiles)

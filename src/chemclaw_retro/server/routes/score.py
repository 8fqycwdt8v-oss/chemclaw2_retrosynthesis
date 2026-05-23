"""Synthesizability / complexity scoring (RAscore + SCScore + SAscore)."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from ...schemas import SynthScoreResponse
from ...scoring.rascore import ra_score
from ...scoring.sascore import sa_score
from ...scoring.scscore import sc_score
from ..auth import require_token

router = APIRouter(tags=["scoring"])


class _ScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    smiles: str = Field(..., description="Target SMILES.")


@router.post(
    "/score/synthesizability",
    response_model=SynthScoreResponse,
    operation_id="score_synthesizability",
    summary="RAscore + SCScore + SAscore for one molecule",
    dependencies=[Depends(require_token)],
)
async def synthesizability(req: _ScoreRequest) -> SynthScoreResponse:
    ra, sc, sa = await asyncio.gather(
        asyncio.to_thread(ra_score, req.smiles),
        asyncio.to_thread(sc_score, req.smiles),
        asyncio.to_thread(sa_score, req.smiles),
    )
    return SynthScoreResponse(smiles=req.smiles, rascore=ra, scscore=sc, sascore=sa)

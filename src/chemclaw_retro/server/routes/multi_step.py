"""Multi-step retrosynthesis route planning.

Phase-1 implementation delegates to a single planner (AiZynthFinder)
running in its own microservice. Phase-3 will fan-out to additional
planners and fuse routes.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ...backends.base import BackendError
from ...backends.registry import all_backends
from ...canonical import canonical_smiles
from ...schemas import MultiStepRequest, MultiStepResponse, Route
from ..auth import require_token

log = logging.getLogger(__name__)
router = APIRouter(tags=["retrosynthesis"])


@router.post(
    "/retrosynthesis/multi_step",
    response_model=MultiStepResponse,
    operation_id="retrosynthesis_multi_step",
    summary="Multi-step retrosynthetic route planning back to stock",
    dependencies=[Depends(require_token)],
)
async def multi_step(req: MultiStepRequest) -> MultiStepResponse:
    try:
        canon_target = canonical_smiles(req.smiles)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    backends = all_backends()
    name = "aizynth" if req.planner == "auto" else req.planner
    if name not in backends:
        raise HTTPException(status_code=503, detail=f"planner '{name}' not enabled")

    planner = backends[name]
    try:
        # Multi-step planners expose /plan via the same RemoteBackend client;
        # the protocol mirrors /predict but with the MultiStep request body.
        resp = await planner._request(  # type: ignore[attr-defined]
            "POST",
            "/plan",
            json=req.model_dump(),
        )
        data = resp.json()
        routes = [Route.model_validate(r) for r in data.get("routes", [])]
    except BackendError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return MultiStepResponse(
        target=canon_target, routes=routes[: req.top_k_routes], planners_used=[name]
    )

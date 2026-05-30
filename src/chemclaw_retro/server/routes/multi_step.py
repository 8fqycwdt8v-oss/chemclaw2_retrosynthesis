"""Multi-step retrosynthesis route planning.

Phase-1 delegated to a single planner (AiZynthFinder). Phase-3+ supports
every backend in :mod:`chemclaw_retro.backends.adapters._catalogue` that
advertises ``capabilities=['multi_step']``. The route picks the planner
from the live registry rather than a schema Literal so adding a new
planner does not require a schema bump.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ...backends.adapters._catalogue import CATALOGUE
from ...backends.base import BackendError, MultiStepPlanner
from ...backends.registry import all_backends
from ...canonical import canonical_smiles
from ...schemas import MultiStepRequest, MultiStepResponse, Route
from ..auth import require_token

log = logging.getLogger(__name__)
router = APIRouter(tags=["retrosynthesis"])


def _resolve_planner(requested: str, available: dict[str, object]) -> str:
    """Resolve ``planner`` to an enabled backend name advertising multi-step.

    'auto' picks the alphabetically-first enabled multi-step backend so
    the choice is deterministic across processes with the same config.
    """
    multi_step_capable = {
        name
        for name, info in CATALOGUE.items()
        if "multi_step" in info.capabilities and name in available
    }
    if requested == "auto":
        picked = min(multi_step_capable, default=None)
        if picked is None:
            raise HTTPException(503, "no multi-step planner enabled")
        return picked
    if requested not in available:
        raise HTTPException(503, f"planner '{requested}' not enabled")
    if requested not in multi_step_capable:
        raise HTTPException(400, f"planner '{requested}' does not advertise multi_step capability")
    return requested


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

    available = all_backends()
    name = _resolve_planner(req.planner, available)
    planner = available[name]

    if not isinstance(planner, MultiStepPlanner):
        raise HTTPException(
            500,
            f"planner '{name}' is registered but does not implement the "
            "MultiStepPlanner contract; capability='multi_step' is out of "
            "sync with the registered adapter.",
        )

    try:
        raw_routes = await planner.plan(
            canon_target,
            max_depth=req.max_depth,
            stock=req.stock,
            top_k_routes=req.top_k_routes,
        )
        routes = [Route.model_validate(r) for r in raw_routes]
    except BackendError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return MultiStepResponse(
        target=canon_target, routes=routes[: req.top_k_routes], planners_used=[name]
    )

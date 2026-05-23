"""Single-step retrosynthesis meta endpoint — fan out to every enabled
backend, aggregate via the meta-reranker, return MetaPrediction list."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ...backends.base import BackendError, SingleStepBackend
from ...backends.registry import select_backends
from ...canonical import canonical_smiles
from ...config import get_settings
from ...forward.round_trip import round_trip_ok
from ...meta.aggregator import aggregate
from ...meta.reranker import HeuristicReranker
from ...schemas import (
    SinglePrediction,
    SingleStepRequest,
    SingleStepResponse,
)
from ...scoring.api import rascore_min, scscore_max
from ..auth import require_token

log = logging.getLogger(__name__)
router = APIRouter(tags=["retrosynthesis"])


def _reranker() -> HeuristicReranker:
    settings = get_settings()
    return HeuristicReranker.from_yaml(Path(settings.weights_path))


async def _query_one(
    backend: SingleStepBackend, smiles: str, top_k: int
) -> tuple[str, list[SinglePrediction] | BackendError]:
    try:
        preds = await backend.predict(smiles, top_k=top_k)
        return backend.name, preds
    except BackendError as e:
        log.warning("backend %s failed: %s", backend.name, e)
        return backend.name, e
    except Exception as e:  # pragma: no cover — defensive
        log.exception("backend %s raised unexpected error", backend.name)
        return backend.name, BackendError(backend.name, str(e), cause=e)


@router.post(
    "/retrosynthesis/single_step",
    response_model=SingleStepResponse,
    operation_id="retrosynthesis_single_step",
    summary="Meta single-step retrosynthesis (ensemble of all enabled backends)",
    dependencies=[Depends(require_token)],
)
async def single_step(req: SingleStepRequest) -> SingleStepResponse:
    """Disconnect ``smiles`` one step retrosynthetically, returning the
    aggregated top-K reactant proposals with full per-backend provenance.

    The aggregator combines reciprocal-rank fusion across backends with
    consensus-counting, RAscore-based synthesisability boost, and (if
    requested) a forward-model round-trip filter.
    """
    try:
        canon_target = canonical_smiles(req.smiles)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    backends = select_backends(req.backends)
    if not backends:
        raise HTTPException(status_code=503, detail="no backends enabled")

    settings = get_settings()
    results = await asyncio.wait_for(
        asyncio.gather(*(_query_one(b, canon_target, req.per_backend_top_k) for b in backends)),
        timeout=settings.overall_timeout_s,
    )

    per_backend: dict[str, list[SinglePrediction]] = {}
    failed: list[str] = []
    for name, outcome in results:
        if isinstance(outcome, BackendError):
            failed.append(name)
        else:
            per_backend[name] = outcome

    forward_checker = None
    if req.run_round_trip:
        from ...backends.remote import RemoteBackend

        fwd = RemoteBackend("forward", settings.forward_url, timeout_s=60.0)

        async def _rt(target: str, reactants: list[str]) -> bool:
            return await round_trip_ok(target, reactants, forward=fwd)

        forward_checker = _rt

    reranker = _reranker()
    meta = await aggregate(
        canon_target,
        per_backend,
        reranker=reranker,
        top_k=req.top_k,
        forward_checker=forward_checker,
        rascorer=rascore_min,
        scscorer=scscore_max,
    )

    return SingleStepResponse(
        target=canon_target,
        results=meta,
        backends_queried=[b.name for b in backends],
        backends_failed=failed,
        degraded=bool(failed),
    )

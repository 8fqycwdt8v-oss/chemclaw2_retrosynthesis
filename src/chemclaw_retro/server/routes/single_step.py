"""Single-step retrosynthesis meta endpoint — fan out to every enabled
backend, aggregate via the meta-reranker, return MetaPrediction list."""

from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ...backends.base import BackendError, SingleStepBackend
from ...backends.registry import select_backends
from ...backends.remote import RemoteBackend
from ...canonical import canonical_smiles
from ...config import get_settings
from ...forward.round_trip import round_trip_ok
from ...meta.aggregator import aggregate
from ...meta.reranker import HeuristicReranker, Reranker
from ...schemas import (
    SinglePrediction,
    SingleStepRequest,
    SingleStepResponse,
)
from ...scoring.api import rascore_min, scscore_max
from ..auth import require_token

log = logging.getLogger(__name__)
router = APIRouter(tags=["retrosynthesis"])


@lru_cache(maxsize=1)
def _reranker() -> Reranker:
    """Build the reranker once per process. Fails loudly on misconfig so
    operators don't silently fall back to the heuristic when they
    intended to use the learned ranker.
    """
    settings = get_settings()
    mode = settings.reranker
    if mode == "learned":
        if settings.learned_model is None:
            raise RuntimeError(
                "CHEMCLAW_RETRO_RERANKER=learned but CHEMCLAW_RETRO_LEARNED_MODEL "
                "is not set; refusing to silently fall back to the heuristic"
            )
        from ...meta.learned_reranker import LearnedReranker

        return LearnedReranker.from_joblib(Path(settings.learned_model))
    if mode != "heuristic":
        raise RuntimeError(
            f"CHEMCLAW_RETRO_RERANKER={mode!r} is not one of 'heuristic' or 'learned'"
        )
    return HeuristicReranker.from_yaml(Path(settings.weights_path))


def reset_reranker_cache() -> None:
    """Test hook — drop the cached reranker so settings changes take effect."""
    _reranker.cache_clear()


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


async def _query_one_bounded(
    backend: SingleStepBackend, smiles: str, top_k: int, timeout_s: float
) -> tuple[str, list[SinglePrediction] | BackendError]:
    """Per-backend timeout so a single slow backend cannot break the
    whole gather. TimeoutError is converted to BackendError so the
    aggregator path stays uniform.
    """
    try:
        return await asyncio.wait_for(_query_one(backend, smiles, top_k), timeout=timeout_s)
    except asyncio.TimeoutError:
        log.warning("backend %s timed out after %.1fs", backend.name, timeout_s)
        return backend.name, BackendError(backend.name, f"timed out after {timeout_s}s")


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

    # Per-backend timeout, not gather-wide: one slow backend cancels
    # only itself; the rest finish and the request returns a degraded
    # response instead of a 500.
    results = await asyncio.gather(
        *(
            _query_one_bounded(b, canon_target, req.per_backend_top_k, settings.overall_timeout_s)
            for b in backends
        )
    )

    per_backend: dict[str, list[SinglePrediction]] = {}
    failed: list[str] = []
    for name, outcome in results:
        if isinstance(outcome, BackendError):
            failed.append(name)
        else:
            per_backend[name] = outcome

    forward_checker = None
    fwd_client: httpx.AsyncClient | None = None
    if req.run_round_trip:
        # Single AsyncClient shared across every round-trip call this
        # request makes — avoids opening N TCP/TLS connections per
        # candidate group.
        fwd_client = httpx.AsyncClient(timeout=settings.round_trip_timeout_s)
        fwd = RemoteBackend(
            "forward",
            settings.forward_url,
            timeout_s=settings.round_trip_timeout_s,
            client=fwd_client,
        )

        async def _rt(target: str, reactants: list[str]) -> bool:
            return await round_trip_ok(target, reactants, forward=fwd)

        forward_checker = _rt

    try:
        reranker = _reranker()
        meta = await asyncio.wait_for(
            aggregate(
                canon_target,
                per_backend,
                reranker=reranker,
                top_k=req.top_k,
                forward_checker=forward_checker,
                rascorer=rascore_min,
                scscorer=scscore_max,
            ),
            timeout=settings.aggregate_timeout_s,
        )
    except asyncio.TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"aggregation exceeded aggregate_timeout_s={settings.aggregate_timeout_s}s",
        ) from e
    finally:
        if fwd_client is not None:
            await fwd_client.aclose()

    return SingleStepResponse(
        target=canon_target,
        results=meta,
        backends_queried=[b.name for b in backends],
        backends_failed=failed,
        degraded=bool(failed),
    )

"""Meta / introspection endpoints."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from ... import __version__
from ...backends.adapters._catalogue import CATALOGUE
from ...backends.registry import all_backends
from ...schemas import BackendInfo

router = APIRouter(tags=["meta"])


@router.get("/healthz", operation_id="healthz", summary="Liveness probe")
async def healthz() -> dict[str, bool]:
    return {"ok": True}


@router.get("/version", operation_id="version", summary="Gateway version")
async def version() -> dict[str, str]:
    return {"version": __version__}


@router.get(
    "/backends",
    response_model=list[BackendInfo],
    operation_id="backends_list",
    summary=(
        "List every wrapped backend with status, license, capabilities, "
        "and citation — both enabled (live status from the container) "
        "and disabled (catalogue metadata only, enabled=false, "
        "healthy=false)."
    ),
)
async def backends_list() -> list[BackendInfo]:
    enabled = all_backends()

    async def _live(name: str, b: object) -> BackendInfo:
        catalogue_info = CATALOGUE.get(name)
        try:
            # info() and healthz() are independent round-trips; fire
            # them concurrently so /backends scales O(1) round-trips
            # in latency instead of O(N).
            info, healthy = await asyncio.gather(
                b.info(),  # type: ignore[attr-defined]
                b.healthz(),  # type: ignore[attr-defined]
            )
            info.healthy = healthy
            info.enabled = True
            return info
        except Exception:
            if catalogue_info is not None:
                return catalogue_info.model_copy(update={"enabled": True, "healthy": False})
            return BackendInfo(
                name=name,
                family="planner",
                license="unknown",
                capabilities=["single_step"],
                enabled=True,
                healthy=False,
            )

    live_results = await asyncio.gather(*(_live(n, b) for n, b in enabled.items()))

    # Backends in the catalogue that aren't enabled: still surfaced so
    # the chemclaw2 agent can see the full menu and per-backend license.
    not_enabled = [
        info.model_copy(update={"enabled": False, "healthy": False})
        for name, info in CATALOGUE.items()
        if name not in enabled
    ]

    return [*live_results, *not_enabled]

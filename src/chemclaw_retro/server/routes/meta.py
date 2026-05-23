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
    summary="List enabled backends with status, license, and capabilities",
)
async def backends_list() -> list[BackendInfo]:
    backends = all_backends()
    results: list[BackendInfo] = []

    async def _safe(name: str, b) -> BackendInfo:
        catalogue_info = CATALOGUE.get(name)
        try:
            info = await b.info()
            info.healthy = await b.healthz()
            return info
        except Exception:
            if catalogue_info is not None:
                return catalogue_info.model_copy(update={"healthy": False})
            return BackendInfo(
                name=name,
                family="planner",
                license="unknown",
                capabilities=["single_step"],
                enabled=True,
                healthy=False,
            )

    results = await asyncio.gather(*(_safe(n, b) for n, b in backends.items()))
    return list(results)

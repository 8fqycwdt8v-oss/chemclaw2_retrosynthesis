"""Async wrappers over the synchronous scorers — run in a thread so they
don't block the FastAPI event loop."""

from __future__ import annotations

import asyncio

from .rascore import ra_score
from .sascore import sa_score
from .scscore import sc_score


async def rascore_min(reactants: list[str]) -> float | None:
    values: list[float] = []
    for s in reactants:
        v = await asyncio.to_thread(ra_score, s)
        if v is not None:
            values.append(v)
    return min(values) if values else None


async def scscore_max(reactants: list[str]) -> float | None:
    values: list[float] = []
    for s in reactants:
        v = await asyncio.to_thread(sc_score, s)
        if v is not None:
            values.append(v)
    return max(values) if values else None


async def sascore_max(reactants: list[str]) -> float | None:
    values: list[float] = []
    for s in reactants:
        v = await asyncio.to_thread(sa_score, s)
        if v is not None:
            values.append(v)
    return max(values) if values else None

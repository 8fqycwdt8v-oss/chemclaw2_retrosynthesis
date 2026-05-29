"""Async wrappers over the synchronous scorers — run in a thread so they
don't block the FastAPI event loop. Reactants within a group are scored
in parallel; group-level fan-out is the aggregator's job."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from .rascore import ra_score
from .sascore import sa_score
from .scscore import sc_score


async def _reduce_per_reactant(
    fn: Callable[[str], float | None],
    reactants: list[str],
    reducer: Callable[[list[float]], float],
) -> float | None:
    values = await asyncio.gather(*(asyncio.to_thread(fn, s) for s in reactants))
    kept = [v for v in values if v is not None]
    return reducer(kept) if kept else None


async def rascore_min(reactants: list[str]) -> float | None:
    return await _reduce_per_reactant(ra_score, reactants, min)


async def scscore_max(reactants: list[str]) -> float | None:
    return await _reduce_per_reactant(sc_score, reactants, max)


async def sascore_max(reactants: list[str]) -> float | None:
    return await _reduce_per_reactant(sa_score, reactants, max)

"""Round-trip consensus filter.

Given a target product and a candidate reactant set, hand the reactants
to a forward synthesis backend and check whether any of the top-K
predicted products canonically matches the target.
"""

from __future__ import annotations

import logging

from ..canonical import canonical_smiles
from ..schemas import ForwardRequest

log = logging.getLogger(__name__)


async def round_trip_ok(
    target_canonical: str, reactants: list[str], *, forward, top_k: int = 3
) -> bool:
    """Returns True iff the forward backend reproduces ``target_canonical``."""
    try:
        products = await forward.forward(ForwardRequest(reactants=reactants, top_k=top_k))
    except Exception as e:  # pragma: no cover — degraded mode handled upstream
        log.debug("round-trip forward call failed: %s", e)
        return False
    for p in products:
        try:
            if canonical_smiles(p.smiles) == target_canonical:
                return True
        except ValueError:
            continue
    return False

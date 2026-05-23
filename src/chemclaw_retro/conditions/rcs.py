"""Phase-1 stub for reaction conditions.

The full Parrot / Reaction-Condition-Selector wrappers will live in their
own containers (Phase 3); for now we degrade gracefully so the route is
queryable end-to-end."""

from __future__ import annotations

from ..schemas import Conditions


async def recommend_conditions(rxn_smiles: str) -> Conditions:
    return Conditions(rxn_smiles=rxn_smiles)

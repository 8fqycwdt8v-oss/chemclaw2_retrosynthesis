"""Rxn-INSIGHT — open-source reaction naming + classification."""

from __future__ import annotations

import asyncio
import logging

log = logging.getLogger(__name__)


async def classify_insight(rxn_smiles: str) -> dict[str, str | None]:
    def _run() -> dict[str, str | None]:
        try:
            from rxn_insight.reaction import Reaction  # type: ignore[import-not-found]
        except Exception as e:  # pragma: no cover
            log.debug("Rxn-INSIGHT unavailable: %s", e)
            return {"name": None, "class": None}
        try:
            r = Reaction(rxn_smiles)
            return {"name": r.get_reaction_name(), "class": r.get_reaction_class()}
        except Exception as e:  # pragma: no cover
            log.debug("Rxn-INSIGHT failed on %s: %s", rxn_smiles, e)
            return {"name": None, "class": None}

    return await asyncio.to_thread(_run)

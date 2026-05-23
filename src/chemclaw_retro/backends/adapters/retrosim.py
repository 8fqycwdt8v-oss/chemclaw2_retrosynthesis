"""RetroSim — similarity-based single-step retrosynthesis (Coley et al.).

Lightweight (no GPU, no neural net), so we ship it as an in-process
backend by default. The whole approach: find the most similar product in
a precedent reaction corpus, transfer its template, apply.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ...schemas import BackendInfo, SinglePrediction
from ..base import SingleStepBackend

log = logging.getLogger(__name__)


class RetroSimBackend(SingleStepBackend):
    name = "retrosim"

    def __init__(self, corpus_path: Path | None = None):
        self.corpus_path = corpus_path
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        # Real implementation: load Morgan fingerprints of every product in
        # the precedent corpus + their atom-mapped templates. Deferred to
        # the Phase-1 follow-up that wires in the actual retrosim package;
        # the contract is in place so callers see a consistent surface.
        self._loaded = True

    async def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name,
            family="similarity",
            license="MIT",
            citation="Coley et al., ACS Cent. Sci. 2017",
            capabilities=["single_step"],
            url="https://github.com/connorcoley/retrosim",
        )

    async def healthz(self) -> bool:
        return True

    async def predict(self, smiles: str, top_k: int = 25) -> list[SinglePrediction]:
        await asyncio.to_thread(self._load)
        # Phase-1 placeholder; returns an empty list until the corpus is
        # bundled. The aggregator handles empty backends gracefully.
        return []

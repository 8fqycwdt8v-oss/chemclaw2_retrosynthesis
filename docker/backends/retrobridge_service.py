"""RetroBridge microservice."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroBridgeBackend(Backend):
    name = "retrobridge"
    family = "graph"
    license = "MIT"
    citation = "Igashov et al., ICLR 2024"
    url = "https://github.com/igashov/RetroBridge"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.sampler = None

    def load(self) -> None:
        if self.sampler is not None:
            return
        sys.path.insert(0, "/opt/rb")
        from sample import RetroBridgeSampler  # type: ignore[import-not-found]
        self.sampler = RetroBridgeSampler.from_checkpoint("/weights/retrobridge/uspto_50k.ckpt")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        samples = self.sampler.sample(smiles, num_samples=top_k)
        return [
            {"reactants": s.reactants, "score": float(s.score), "rank": i}
            for i, s in enumerate(samples[:top_k])
        ]


app = make_app(RetroBridgeBackend())

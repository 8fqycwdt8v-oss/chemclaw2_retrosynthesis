"""Het-retro service — heterocycle-specialised single-step retrosynthesis."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class HetRetroBackend(Backend):
    name = "het_retro"
    family = "transformer"
    license = "MIT"
    citation = "Duarte group, 2025"
    url = "https://github.com/duartegroup/Het-retro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/het")
        from het_retro.predictor import HetRetroPredictor  # type: ignore[import-not-found]
        self.model = HetRetroPredictor.load("/weights/het_retro/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model.predict(smiles, top_k=top_k)
        return [
            {"reactants": h["reactants"].split("."), "score": float(h["score"]), "rank": i}
            for i, h in enumerate(out[:top_k])
        ]


app = make_app(HetRetroBackend())

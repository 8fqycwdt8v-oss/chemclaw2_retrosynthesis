"""Disconnection-aware Chemformer service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class DisconnectionChemformerBackend(Backend):
    name = "disconnection_chemformer"
    family = "transformer"
    license = "MIT"
    citation = "Thakkar et al., Chem. Sci. 2023"
    url = "https://github.com/rxn4chemistry/disconnection_aware_retrosynthesis"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/dac")
        from disconnection_aware.predict import DisconnectionPredictor  # type: ignore[import-not-found]
        self.model = DisconnectionPredictor.load("/weights/disconnection_chemformer/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model(smiles, top_k=top_k)
        return [
            {"reactants": p["reactants"], "score": float(p["score"]), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(DisconnectionChemformerBackend())

"""NeuralSym service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class NeuralSymBackend(Backend):
    name = "neuralsym"
    family = "template"
    license = "MIT"
    citation = "Segler & Waller, Chem. Eur. J. 2017 (reimpl.)"
    url = "https://github.com/linminhtoo/neuralsym"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.predictor = None

    def load(self) -> None:
        if self.predictor is not None:
            return
        sys.path.insert(0, "/opt/ns")
        from neuralsym.predict import NeuralSymPredictor  # type: ignore[import-not-found]
        self.predictor = NeuralSymPredictor.from_checkpoint("/weights/neuralsym/elu_512.pt")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.predictor(smiles, top_k=top_k)
        return [
            {
                "reactants": p["reactants"].split("."),
                "score": float(p["score"]),
                "rank": i,
                "template_id": str(p.get("template_id", "")),
            }
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(NeuralSymBackend())

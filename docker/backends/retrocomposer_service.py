"""RetroComposer service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroComposerBackend(Backend):
    name = "retrocomposer"
    family = "template"
    license = "MIT"
    citation = "Yan et al., Biomolecules 2022"
    url = "https://github.com/uta-smile/RetroComposer"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.predictor = None

    def load(self) -> None:
        if self.predictor is not None:
            return
        sys.path.insert(0, "/opt/rc")
        from retrocomposer.predict import RetroComposerPredictor  # type: ignore[import-not-found]
        self.predictor = RetroComposerPredictor.load("/weights/retrocomposer/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.predictor(smiles, top_k=top_k)
        return [
            {"reactants": h["reactants"].split("."), "score": float(h["score"]), "rank": i}
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(RetroComposerBackend())

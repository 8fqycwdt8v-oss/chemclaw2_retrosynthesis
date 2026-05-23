"""RetroXpert service. FLAG: see adapter docstring re: information-leak.
Run only after confirming the leak-fix branch is checked out."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroXpertBackend(Backend):
    name = "retroxpert"
    family = "transformer"
    license = "MIT"
    citation = "Yan et al., NeurIPS 2020 (FLAG: information-leak disclosed)"
    url = "https://github.com/uta-smile/RetroXpert"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/rx")
        from retroxpert.predict import RetroXpert  # type: ignore[import-not-found]
        self.model = RetroXpert.load("/weights/retroxpert/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model(smiles, top_k=top_k)
        return [
            {"reactants": p["reactants"].split("."), "score": float(p["score"]), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(RetroXpertBackend())

"""RetroChimera microservice."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroChimeraBackend(Backend):
    name = "retrochimera"
    family = "hybrid"
    license = "MIT"
    citation = "Maziarz et al., arXiv:2412.05269"
    url = "https://github.com/microsoft/retrochimera"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/chimera")
        from retrochimera.api import Chimera  # type: ignore[import-not-found]
        self.model = Chimera.load("/weights/retrochimera")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.model.predict(smiles, top_k=top_k)
        return [
            {"reactants": h.reactants, "score": float(h.score), "rank": i}
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(RetroChimeraBackend())

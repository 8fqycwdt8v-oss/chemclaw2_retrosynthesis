"""RetroPrime service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroPrimeBackend(Backend):
    name = "retroprime"
    family = "transformer"
    license = "MIT"
    citation = "Wang et al., Chem. Eng. J. 2021"
    url = "https://github.com/wangxr0526/RetroPrime"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/rp")
        from retroprime.predict import RetroPrime  # type: ignore[import-not-found]
        self.model = RetroPrime.load("/weights/retroprime/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model(smiles, beam_size=top_k)
        return [
            {"reactants": p["reactants"].split("."), "score": float(p["score"]), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(RetroPrimeBackend())

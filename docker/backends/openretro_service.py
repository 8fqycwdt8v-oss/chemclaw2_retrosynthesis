"""OpenRetro service. Set OPENRETRO_MODEL to pick a model (gln,
neuralsym, retroxpert, transformer)."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class OpenRetroBackend(Backend):
    name = "openretro"
    family = "planner"
    license = "MIT"
    citation = "Coley group"
    url = "https://github.com/coleygroup/openretro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/openretro")
        from openretro.serve import load_model  # type: ignore[import-not-found]
        name = os.environ.get("OPENRETRO_MODEL", "transformer")
        self.model = load_model(name, weights="/weights/openretro/")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model(smiles, top_k=top_k)
        return [
            {"reactants": p["reactants"].split("."), "score": float(p["score"]), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(OpenRetroBackend())

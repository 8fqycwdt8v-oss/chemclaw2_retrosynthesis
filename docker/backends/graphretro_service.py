"""GraphRetro service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class GraphRetroBackend(Backend):
    name = "graphretro"
    family = "graph"
    license = "MIT"
    citation = "Somnath et al., NeurIPS 2021"
    url = "https://github.com/vsomnath/graphretro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/gr")
        from graphretro.eval import load_model_from_checkpoint  # type: ignore[import-not-found]
        self.model = load_model_from_checkpoint("/weights/graphretro/model.pt")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model.predict(smiles, top_k=top_k)
        return [
            {"reactants": p.reactants, "score": float(p.score), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(GraphRetroBackend())

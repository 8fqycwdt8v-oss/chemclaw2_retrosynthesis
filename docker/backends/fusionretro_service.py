"""FusionRetro service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class FusionRetroBackend(Backend):
    name = "fusionretro"
    family = "transformer"
    license = "MIT"
    citation = "Liu et al., ICML 2023"
    url = "https://github.com/SongtaoLiu0823/FusionRetro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/fr")
        from fusionretro.predict import FusionRetro  # type: ignore[import-not-found]
        self.model = FusionRetro.from_checkpoint("/weights/fusionretro/uspto_50k.pt")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model.predict(smiles, beam_size=top_k)
        return [
            {"reactants": p.reactants, "score": float(p.score), "rank": i}
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(FusionRetroBackend())

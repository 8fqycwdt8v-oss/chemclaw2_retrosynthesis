"""G2Retro service. Set G2RETRO_ENSEMBLE=1 to use the ensemble variant."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class G2RetroBackend(Backend):
    name = "g2retro"
    family = "graph"
    license = "MIT"
    citation = "Chen & Zhang, Nat. Commun. 2023"
    url = "https://github.com/yhwwang/G2Retro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/g2r")
        from g2retro.predictor import Predictor  # type: ignore[import-not-found]
        ckpt = "/weights/g2retro/model_ens.pt" if os.environ.get("G2RETRO_ENSEMBLE") == "1" else "/weights/g2retro/model.pt"
        self.model = Predictor.load(ckpt)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.model.predict(smiles, top_k=top_k)
        return [
            {"reactants": h["reactants"], "score": float(h["score"]), "rank": i}
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(G2RetroBackend())

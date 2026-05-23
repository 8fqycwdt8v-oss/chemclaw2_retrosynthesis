"""Retroformer service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class RetroformerBackend(Backend):
    name = "retroformer"
    family = "transformer"
    license = "MIT"
    citation = "Wan et al., ICML 2022"
    url = "https://github.com/yuewan2/Retroformer"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/rfm")
        from translate import load_model  # type: ignore[import-not-found]
        self.model = load_model("/weights/retroformer/checkpoint.pt")

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        preds = self.model.translate([smiles], beam_size=top_k, n_best=top_k)[0]
        return [
            {"reactants": p["pred"].split("."), "score": float(p["score"]), "rank": i}
            for i, p in enumerate(preds[:top_k])
        ]


app = make_app(RetroformerBackend())

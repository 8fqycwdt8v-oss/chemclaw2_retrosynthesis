"""Graph2SMILES microservice — both retro and forward via the same model
class with different checkpoints."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class Graph2SMILESBackend(Backend):
    name = "graph2smiles"
    family = "graph"
    license = "MIT"
    citation = "Tu & Coley, JCIM 2022"
    url = "https://github.com/coleygroup/Graph2SMILES"
    capabilities = ["single_step", "forward"]

    def __init__(self) -> None:
        self.retro = None
        self.forward_model = None

    def load(self) -> None:
        if self.retro is not None:
            return
        sys.path.insert(0, "/opt/g2s")
        from translate import load_translator  # type: ignore[import-not-found]
        retro_ckpt = os.environ.get(
            "G2S_RETRO_CKPT", "/weights/graph2smiles/uspto_50k_retro.pt"
        )
        fwd_ckpt = os.environ.get(
            "G2S_FORWARD_CKPT", "/weights/graph2smiles/uspto_480k_forward.pt"
        )
        self.retro = load_translator(retro_ckpt)
        self.forward_model = load_translator(fwd_ckpt)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        preds = self.retro.translate([smiles], n_best=top_k)[0]
        return [
            {"reactants": p["pred"].split("."), "score": float(p["score"]), "rank": i}
            for i, p in enumerate(preds[:top_k])
        ]

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        src = ".".join(reactants)
        preds = self.forward_model.translate([src], n_best=top_k)[0]
        return [{"smiles": p["pred"], "score": float(p["score"])} for p in preds[:top_k]]


app = make_app(Graph2SMILESBackend())

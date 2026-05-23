"""MHNreact microservice."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, make_app


class MHNreactBackend(Backend):
    name = "mhnreact"
    family = "template"
    license = "MIT"
    citation = "Seidl et al., NeurIPS 2022 AI4Science"
    url = "https://github.com/ml-jku/mhn-react"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        from mhnreact.model import load_pretrained  # type: ignore[import-not-found]
        ckpt = os.environ.get("MHN_CKPT", "/weights/mhnreact/model.pt")
        self.model = load_pretrained(ckpt)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        from mhnreact.inference import predict_top_k  # type: ignore[import-not-found]
        hits = predict_top_k(self.model, smiles, k=top_k)
        return [
            {
                "reactants": h["reactants"].split("."),
                "score": float(h["score"]),
                "rank": i,
                "template": h.get("template"),
                "template_id": str(h.get("template_id", "")),
            }
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(MHNreactBackend())

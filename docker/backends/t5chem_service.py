"""T5Chem service — multitask (retro + forward + class)."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, make_app


class T5ChemBackend(Backend):
    name = "t5chem"
    family = "transformer"
    license = "MIT"
    citation = "Lu & Zhang, JCIM 2022"
    url = "https://github.com/HelloJocelynLu/t5chem"
    capabilities = ["single_step", "forward"]

    def __init__(self) -> None:
        self.retro = None
        self.fwd = None

    def load(self) -> None:
        if self.retro is not None:
            return
        from t5chem import T5ForProperty  # type: ignore[import-not-found]
        retro_path = os.environ.get("T5CHEM_RETRO", "/weights/t5chem/retrosynthesis")
        fwd_path = os.environ.get("T5CHEM_FORWARD", "/weights/t5chem/product")
        self.retro = T5ForProperty.from_pretrained(retro_path)
        self.fwd = T5ForProperty.from_pretrained(fwd_path)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        preds = self.retro.predict(smiles, num_beams=top_k, num_return_sequences=top_k)
        return [
            {"reactants": p.split("."), "score": 1.0 - i * 0.05, "rank": i}
            for i, p in enumerate(preds[:top_k])
        ]

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        src = ".".join(reactants)
        preds = self.fwd.predict(src, num_beams=top_k, num_return_sequences=top_k)
        return [{"smiles": p, "score": 1.0 - i * 0.05} for i, p in enumerate(preds[:top_k])]


app = make_app(T5ChemBackend())

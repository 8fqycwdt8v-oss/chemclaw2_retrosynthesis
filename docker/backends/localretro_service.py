"""LocalRetro microservice."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class LocalRetroBackend(Backend):
    name = "localretro"
    family = "template"
    license = "Apache-2.0"
    citation = "Chen & Jung, JACS Au 2021"
    url = "https://github.com/kaist-amsg/LocalRetro"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None
        self.templates = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/localretro")
        from scripts.utils import load_model  # type: ignore[import-not-found]
        ckpt = os.environ.get(
            "LOCALRETRO_CKPT", "/weights/localretro/LocalRetro_USPTO_50K.pth"
        )
        tmpl = os.environ.get(
            "LOCALRETRO_TEMPLATES", "/weights/localretro/templates.csv"
        )
        self.model, self.templates = load_model(ckpt, tmpl)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        sys.path.insert(0, "/opt/localretro")
        from scripts.utils import combine_reactants, predict  # type: ignore[import-not-found]
        raw = predict(self.model, smiles, self.templates, top_k=top_k)
        out: list[dict[str, Any]] = []
        for rank, hit in enumerate(raw):
            reactants = combine_reactants(smiles, hit["template"])
            out.append(
                {
                    "reactants": [r for r in reactants if r],
                    "score": float(hit["score"]),
                    "rank": rank,
                    "template": hit["template"],
                    "template_id": str(hit.get("template_id", "")),
                }
            )
        return out


app = make_app(LocalRetroBackend())

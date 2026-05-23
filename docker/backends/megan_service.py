"""MEGAN microservice — Molecule.one's graph-edit attention network."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class MEGANBackend(Backend):
    name = "megan"
    family = "graph"
    license = "MIT"
    citation = "Sacha et al., JCIM 2021"
    url = "https://github.com/molecule-one/megan"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None
        self.featurizer = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/megan")
        from src.config import get_featurizer  # type: ignore[import-not-found]
        from src.feat.megan_graph import MeganGraph  # noqa: F401
        from src.model.megan_model import Megan  # type: ignore[import-not-found]

        ckpt = os.environ.get("MEGAN_CKPT", "/weights/megan/uspto_50k/model_best.pt")
        self.featurizer = get_featurizer("uspto_50k")
        self.model = Megan.load(ckpt)
        self.model.eval()

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        sys.path.insert(0, "/opt/megan")
        from src.model.beam_search import beam_search  # type: ignore[import-not-found]

        results = beam_search(self.model, smiles, beam_size=top_k, featurizer=self.featurizer)
        return [
            {
                "reactants": r["reactants"].split("."),
                "score": float(r["score"]),
                "rank": i,
            }
            for i, r in enumerate(results[:top_k])
        ]


app = make_app(MEGANBackend())

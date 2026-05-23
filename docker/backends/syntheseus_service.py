"""Syntheseus microservice — uses Syntheseus's uniform model wrappers.

The wrapped single-step model is chosen via ``SYNTHESEUS_MODEL`` env
(default: ``chemformer``). Available: ``chemformer``, ``localretro``,
``mhnreact``, ``megan``, ``rootaligned``, ``retroknn``, ``graph2smiles``."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, make_app


class SyntheseusBackend(Backend):
    name = "syntheseus"
    family = "planner"
    license = "MIT"
    citation = "Maziarz et al., Faraday Discuss. 2024"
    url = "https://github.com/microsoft/syntheseus"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        from syntheseus.reaction_prediction.inference import get_model_class  # type: ignore[import-not-found]

        name = os.environ.get("SYNTHESEUS_MODEL", "chemformer")
        weights = os.environ.get("SYNTHESEUS_WEIGHTS", f"/weights/syntheseus/{name}")
        cls = get_model_class(name)
        self.model = cls(weights_dir=weights)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        from syntheseus.interface.molecule import Molecule  # type: ignore[import-not-found]

        outputs = self.model([Molecule(smiles)], num_results=top_k)[0]
        return [
            {
                "reactants": [m.smiles for m in r.reactants],
                "score": float(getattr(r, "probability", 1.0)),
                "rank": i,
            }
            for i, r in enumerate(outputs[:top_k])
        ]


app = make_app(SyntheseusBackend())

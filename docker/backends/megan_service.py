"""MEGAN microservice — Molecule.one's graph-edit attention network.

Upstream API note: ``molecule-one/megan`` does NOT expose a top-level
``Megan.load(path)`` classmethod, and the load API differs between
PyTorch-Lightning .ckpt and v1.1-release model_best.pt formats. We try
the documented paths in order and surface a useful error if none
works, with ``MEGAN_LOADER`` to pin a strategy.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, _try_loaders, make_app


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
        from src.model.megan_model import Megan  # type: ignore[import-not-found]

        ckpt = os.environ.get("MEGAN_CKPT", "/weights/megan/uspto_50k/model_best.pt")
        self.featurizer = get_featurizer("uspto_50k")

        def _via_load_from_checkpoint() -> object:
            return Megan.load_from_checkpoint(ckpt)

        def _via_load() -> object:
            return Megan.load(ckpt)  # type: ignore[attr-defined]

        def _via_state_dict() -> object:
            import torch  # type: ignore[import-not-found]

            state = torch.load(ckpt, map_location="cpu")
            m = Megan(featurizer=self.featurizer)
            m.load_state_dict(state.get("state_dict", state))
            return m

        self.model = _try_loaders(
            [
                ("load_from_checkpoint", _via_load_from_checkpoint),
                ("load", _via_load),
                ("state_dict", _via_state_dict),
            ],
            pin_env="MEGAN_LOADER",
            label="MEGAN model",
        )
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

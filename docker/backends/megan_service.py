"""MEGAN microservice — Molecule.one's graph-edit attention network.

Upstream API note: ``molecule-one/megan`` does NOT expose a top-level
``Megan.load(path)`` classmethod. The actual entry point depends on the
checkpoint format the operator downloads (PyTorch Lightning .ckpt vs
the v1.1-release model_best.pt). We try the documented paths in order
and surface a useful error if none works, so the operator can update
``MEGAN_LOADER`` env to the right call for their checkpoint.
"""

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
        ckpt = os.environ.get("MEGAN_CKPT", "/weights/megan/uspto_50k/model_best.pt")
        loader = os.environ.get("MEGAN_LOADER", "auto")

        from src.config import get_featurizer  # type: ignore[import-not-found]
        from src.model.megan_model import Megan  # type: ignore[import-not-found]

        self.featurizer = get_featurizer("uspto_50k")

        errors: list[str] = []
        for attempt in (loader,) if loader != "auto" else ("load_from_checkpoint", "load", "ctor"):
            try:
                if attempt == "load_from_checkpoint":
                    self.model = Megan.load_from_checkpoint(ckpt)  # PyTorch Lightning
                elif attempt == "load" and hasattr(Megan, "load"):
                    self.model = Megan.load(ckpt)  # type: ignore[attr-defined]
                elif attempt == "ctor":
                    import torch  # type: ignore[import-not-found]

                    state = torch.load(ckpt, map_location="cpu")
                    self.model = Megan(featurizer=self.featurizer)
                    self.model.load_state_dict(state["state_dict"] if "state_dict" in state else state)
                else:
                    continue
                break
            except Exception as e:  # noqa: BLE001
                errors.append(f"{attempt}: {e!r}")
                self.model = None
        if self.model is None:
            raise RuntimeError(
                "MEGAN model load failed for every known upstream entry point. "
                "Set MEGAN_LOADER={load_from_checkpoint|load|ctor} for your "
                "checkpoint format. Tried: " + "; ".join(errors)
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

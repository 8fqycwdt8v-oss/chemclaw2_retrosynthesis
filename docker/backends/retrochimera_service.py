"""RetroChimera microservice.

Upstream Chimera is an internal ensemble (NeuralLoc + R-SMILES 2 +
learned reranker) from Microsoft + Novartis. The public release does
not ship a uniform ``Chimera.load`` classmethod; the loading API
changes across releases. We try the documented constructor patterns
in order, with ``RETROCHIMERA_LOADER`` to pin one.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, _try_loaders, make_app


def _get(h: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` off ``h`` whether it's a dict or an object."""
    if isinstance(h, dict):
        return h.get(key, default)
    return getattr(h, key, default)


class RetroChimeraBackend(Backend):
    name = "retrochimera"
    family = "hybrid"
    license = "MIT"
    citation = "Maziarz et al., arXiv:2412.05269"
    url = "https://github.com/microsoft/retrochimera"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/chimera")
        weights = os.environ.get("RETROCHIMERA_WEIGHTS", "/weights/retrochimera")
        if not os.path.isdir(weights):
            raise RuntimeError(
                f"RETROCHIMERA_WEIGHTS={weights} does not exist; "
                "download per https://github.com/microsoft/retrochimera README"
            )

        def _via_api_load() -> object:
            from retrochimera.api import Chimera  # type: ignore[import-not-found]

            return Chimera.load(weights) if hasattr(Chimera, "load") else Chimera(weights)

        def _via_ensemble() -> object:
            from chimera.ensemble import EnsembleModel  # type: ignore[import-not-found]

            return EnsembleModel.from_pretrained(weights)

        self.model = _try_loaders(
            [("api", _via_api_load), ("ensemble", _via_ensemble)],
            pin_env="RETROCHIMERA_LOADER",
            label="RetroChimera",
        )

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.model.predict(smiles, top_k=top_k)
        return [
            {
                "reactants": _get(h, "reactants"),
                "score": float(_get(h, "score", 0.0)),
                "rank": i,
            }
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(RetroChimeraBackend())

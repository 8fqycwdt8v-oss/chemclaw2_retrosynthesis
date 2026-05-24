"""RetroChimera microservice.

Upstream note: Chimera is an internal ensemble (NeuralLoc + R-SMILES 2
+ learned reranker) from Microsoft + Novartis. The public release does
not ship a uniform ``Chimera.load`` classmethod; the loading API
changes across releases. This service tries the documented constructor
patterns in order and fails loudly with a clear message so the
operator can update ``RETROCHIMERA_LOADER``.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


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

        errors: list[str] = []
        # Try the documented entry points in order.
        try:
            from retrochimera.api import Chimera  # type: ignore[import-not-found]

            self.model = Chimera.load(weights) if hasattr(Chimera, "load") else Chimera(weights)
            return
        except Exception as e:  # noqa: BLE001
            errors.append(f"retrochimera.api.Chimera: {e!r}")

        try:
            from chimera.ensemble import EnsembleModel  # type: ignore[import-not-found]

            self.model = EnsembleModel.from_pretrained(weights)
            return
        except Exception as e:  # noqa: BLE001
            errors.append(f"chimera.ensemble.EnsembleModel: {e!r}")

        raise RuntimeError(
            "RetroChimera load failed for every known upstream entry "
            "point. The upstream package layout changes across releases; "
            "verify the Python API for the installed version and update "
            "docker/backends/retrochimera_service.py. Tried: "
            + "; ".join(errors)
        )

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.model.predict(smiles, top_k=top_k)
        return [
            {"reactants": getattr(h, "reactants", h.get("reactants") if isinstance(h, dict) else None),
             "score": float(getattr(h, "score", h.get("score") if isinstance(h, dict) else 0.0)),
             "rank": i}
            for i, h in enumerate(hits[:top_k])
        ]


app = make_app(RetroChimeraBackend())

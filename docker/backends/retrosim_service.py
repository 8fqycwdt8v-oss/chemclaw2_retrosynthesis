"""RetroSim microservice — similarity-based retrosynthesis."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class RetroSimBackend(Backend):
    name = "retrosim"
    family = "similarity"
    license = "MIT"
    citation = "Coley et al., ACS Cent. Sci. 2017"
    url = "https://github.com/connorcoley/retrosim"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.lib = None

    def load(self) -> None:
        if self.lib is not None:
            return
        sys.path.insert(0, "/opt/retrosim")
        import pandas as pd
        from retrosim.utils.generate_retro_templates import (  # type: ignore[import-not-found]
            process_an_example,  # noqa: F401
        )

        corpus_path = os.environ.get(
            "RETROSIM_CORPUS",
            "/opt/retrosim/retrosim/data/data_processed.csv",
        )
        self.lib = pd.read_csv(corpus_path)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        sys.path.insert(0, "/opt/retrosim")
        from retrosim.run_retro import do_one  # type: ignore[import-not-found]

        out = do_one(smiles, self.lib, max_prec=top_k)
        return [
            {
                "reactants": p["reactants"].split("."),
                "score": float(p["prob"]),
                "rank": i,
                "template": p.get("template"),
            }
            for i, p in enumerate(out[:top_k])
        ]


app = make_app(RetroSimBackend())

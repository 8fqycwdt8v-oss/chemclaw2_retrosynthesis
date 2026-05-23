"""R-SMILES microservice — uses OpenNMT-py's translate engine."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class RSmilesBackend(Backend):
    name = "rsmiles"
    family = "transformer"
    license = "MIT"
    citation = "Zhong et al., Chem. Sci. 2022"
    url = "https://github.com/otori-bird/retrosynthesis"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.translator = None

    def load(self) -> None:
        if self.translator is not None:
            return
        sys.path.insert(0, "/opt/rsmiles")
        from onmt.translate.translator import build_translator  # type: ignore[import-not-found]
        from onmt.utils.parse import ArgumentParser  # type: ignore[import-not-found]

        ckpt = os.environ.get("RSMILES_CKPT", "/weights/rsmiles/USPTO_50K_aug20.pt")
        parser = ArgumentParser()
        parser.add_argument("--model", default=ckpt)
        parser.add_argument("--gpu", type=int, default=0)
        opt = parser.parse_args([])
        self.translator = build_translator(opt, report_score=False)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        # R-SMILES augments inputs and rank-aggregates; for Phase-2 we do
        # a single deterministic pass and beam-search.
        scores, preds = self.translator.translate(src=[smiles], n_best=top_k)
        return [
            {"reactants": p.split("."), "score": float(s), "rank": i}
            for i, (p, s) in enumerate(zip(preds[0][:top_k], scores[0][:top_k]))
        ]


app = make_app(RSmilesBackend())

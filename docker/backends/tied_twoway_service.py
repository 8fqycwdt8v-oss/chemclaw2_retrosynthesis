"""Tied Two-Way Transformer service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, make_app


class TiedTwoWayBackend(Backend):
    name = "tied_twoway"
    family = "transformer"
    license = "MIT"
    citation = "Lee et al., JCIM 2022"
    url = "https://github.com/ejklike/tied-twoway-transformer"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.translator = None

    def load(self) -> None:
        if self.translator is not None:
            return
        sys.path.insert(0, "/opt/ttt")
        from onmt.translate.translator import build_translator  # type: ignore[import-not-found]
        from onmt.utils.parse import ArgumentParser  # type: ignore[import-not-found]
        parser = ArgumentParser()
        parser.add_argument("--model", default="/weights/tied_twoway/model.pt")
        parser.add_argument("--gpu", type=int, default=0)
        self.translator = build_translator(parser.parse_args([]), report_score=False)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        scores, preds = self.translator.translate(src=[smiles], n_best=top_k)
        return [
            {"reactants": p.split("."), "score": float(s), "rank": i}
            for i, (p, s) in enumerate(zip(preds[0][:top_k], scores[0][:top_k]))
        ]


app = make_app(TiedTwoWayBackend())

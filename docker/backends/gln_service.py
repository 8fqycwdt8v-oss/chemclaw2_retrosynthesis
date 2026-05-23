"""GLN microservice."""

from __future__ import annotations

import os
import sys
from typing import Any

from _base import Backend, make_app


class GLNBackend(Backend):
    name = "gln"
    family = "graph"
    license = "MIT"
    citation = "Dai et al., NeurIPS 2019"
    url = "https://github.com/Hanjun-Dai/GLN"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/gln")
        from gln.test.model_inference import RetroGLN  # type: ignore[import-not-found]
        ckpt = os.environ.get("GLN_CKPT", "/weights/gln/model.dump")
        self.model = RetroGLN(dropbox=os.path.dirname(ckpt), model_dump=ckpt)

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        out = self.model.run(smiles, beam_size=top_k, topk=top_k)
        return [
            {
                "reactants": r.split("."),
                "score": float(s),
                "rank": i,
                "template": t,
            }
            for i, (r, s, t) in enumerate(
                zip(out["reactants"], out["scores"], out["template"])
            )
        ]


app = make_app(GLNBackend())

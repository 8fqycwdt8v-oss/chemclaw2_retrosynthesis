"""GLN microservice.

Upstream API note: ``Hanjun-Dai/GLN`` exposes
``gln.test.model_inference.RetroGLN(dropbox, model_for_test)`` (positional,
not kw — and it needs precomputed `cooked_*` artifacts at ``dropbox``).
Earlier the env layout was incorrectly passed as kwargs; the canonical
upstream call is positional. Operators who pre-compute the artifacts
should set ``GLN_DROPBOX`` to the directory containing them and
``GLN_MODEL_DUMP`` to the ``model.dump`` file.
"""

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

        dropbox = os.environ.get("GLN_DROPBOX", "/weights/gln")
        model_dump = os.environ.get("GLN_MODEL_DUMP", "/weights/gln/model.dump")
        for path in (dropbox, model_dump):
            if not os.path.exists(path):
                raise RuntimeError(
                    f"GLN required artifact missing: {path}. Download per "
                    "https://github.com/Hanjun-Dai/GLN README (Dropbox link) "
                    "and place the cooked_* artifacts + model.dump under /weights/gln."
                )
        # Upstream signature is positional (dropbox, model_for_test).
        self.model = RetroGLN(dropbox, model_dump)

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

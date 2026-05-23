"""DirectMultiStep microservice."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, PlanRequest, make_app


class DirectMultiStepBackend(Backend):
    name = "directmultistep"
    family = "planner"
    license = "MIT"
    citation = "Shee et al., JCIM 2025"
    url = "https://github.com/batistagroup/DirectMultiStep"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        from directmultistep import load_model  # type: ignore[import-not-found]
        name = os.environ.get("DMS_MODEL", "DMS-Explorer-XL")
        self.model = load_model(name)

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        routes = self.model.predict(req.smiles, n_beams=req.top_k_routes)
        out: list[dict[str, Any]] = []
        for r in routes:
            steps = [
                {
                    "product": s.product,
                    "reactants": s.reactants,
                    "backend": "directmultistep",
                    "score": float(getattr(r, "score", 0.0)),
                }
                for s in r.steps
            ]
            leaves = r.leaves if hasattr(r, "leaves") else [s.reactants[-1] for s in r.steps]
            out.append(
                {
                    "target": req.smiles,
                    "steps": steps,
                    "leaves": leaves,
                    "in_stock_fraction": float(getattr(r, "in_stock_fraction", 0.0)),
                    "depth": len(steps),
                    "final_score": float(getattr(r, "score", 0.0)),
                    "planner": "directmultistep",
                }
            )
        return out


app = make_app(DirectMultiStepBackend())

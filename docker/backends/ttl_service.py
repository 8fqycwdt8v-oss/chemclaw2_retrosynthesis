"""Triple Transformer Loop service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class TTLBackend(Backend):
    name = "ttl"
    family = "planner"
    license = "MIT"
    citation = "Andronov et al., Chem. Sci. 2023"
    url = "https://github.com/reymond-group/MultiStepRetrosynthesisTTL"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.engine = None

    def load(self) -> None:
        if self.engine is not None:
            return
        sys.path.insert(0, "/opt/ttl")
        from ttl_retrosynthesis.engine import TTLEngine  # type: ignore[import-not-found]
        self.engine = TTLEngine()

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        routes = self.engine.plan(req.smiles, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": r.steps,
                "leaves": r.leaves,
                "in_stock_fraction": float(r.in_stock_fraction),
                "depth": len(r.steps),
                "final_score": float(r.score),
                "planner": "ttl",
            }
            for r in routes[: req.top_k_routes]
        ]


app = make_app(TTLBackend())

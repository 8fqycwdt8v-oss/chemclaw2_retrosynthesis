"""DESP microservice."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class DESPBackend(Backend):
    name = "desp"
    family = "planner"
    license = "MIT"
    citation = "Yu et al., NeurIPS 2024"
    url = "https://github.com/coleygroup/desp"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.planner = None

    def load(self) -> None:
        if self.planner is not None:
            return
        sys.path.insert(0, "/opt/desp")
        from desp.planner import DESPPlanner  # type: ignore[import-not-found]
        self.planner = DESPPlanner()

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        routes = self.planner.plan(req.smiles, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": [s.to_dict() for s in r.steps],
                "leaves": r.leaves,
                "in_stock_fraction": float(r.in_stock_fraction),
                "depth": len(r.steps),
                "final_score": float(r.score),
                "planner": "desp",
            }
            for r in routes[: req.top_k_routes]
        ]


app = make_app(DESPBackend())

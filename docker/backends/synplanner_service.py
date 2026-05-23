"""SynPlanner service."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, PlanRequest, make_app


class SynPlannerBackend(Backend):
    name = "synplanner"
    family = "planner"
    license = "MIT"
    citation = "Tagirov et al., JCIM 2025"
    url = "https://github.com/Laboratoire-de-Chemoinformatique/SynPlanner"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.planner = None

    def load(self) -> None:
        if self.planner is not None:
            return
        from synplanner.planner import SynPlanner  # type: ignore[import-not-found]
        cfg = os.environ.get("SYNPLANNER_CONFIG", "/weights/synplanner/config.yaml")
        self.planner = SynPlanner.from_config(cfg)

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        routes = self.planner.plan(req.smiles, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": r.steps,
                "leaves": r.leaves,
                "in_stock_fraction": float(r.in_stock_fraction),
                "depth": len(r.steps),
                "final_score": float(r.score),
                "planner": "synplanner",
            }
            for r in routes[: req.top_k_routes]
        ]


app = make_app(SynPlannerBackend())

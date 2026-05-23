"""READRetro service."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class READRetroBackend(Backend):
    name = "readretro"
    family = "biocatalysis"
    license = "MIT"
    citation = "Lee et al., New Phytol. 2024"
    url = "https://github.com/SeulLee05/READRetro"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.engine = None

    def load(self) -> None:
        if self.engine is not None:
            return
        sys.path.insert(0, "/opt/rr")
        from run import READRetroEngine  # type: ignore[import-not-found]
        self.engine = READRetroEngine()

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        out = self.engine.plan(req.smiles, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": r["steps"],
                "leaves": r["leaves"],
                "in_stock_fraction": float(r.get("in_stock_fraction", 0.0)),
                "depth": len(r["steps"]),
                "final_score": float(r.get("score", 0.0)),
                "planner": "readretro",
            }
            for r in out[: req.top_k_routes]
        ]


app = make_app(READRetroBackend())

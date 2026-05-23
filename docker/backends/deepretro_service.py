"""DeepRetro service — depends on an LLM API key (set ANTHROPIC_API_KEY
or OPENAI_API_KEY)."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class DeepRetroBackend(Backend):
    name = "deepretro"
    family = "hybrid"
    license = "MIT"
    citation = "arXiv:2507.07060"
    url = "https://github.com/deepforestsci/DeepRetro"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.engine = None

    def load(self) -> None:
        if self.engine is not None:
            return
        sys.path.insert(0, "/opt/dr")
        from deepretro.engine import DeepRetroEngine  # type: ignore[import-not-found]
        self.engine = DeepRetroEngine()

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
                "planner": "deepretro",
            }
            for r in routes[: req.top_k_routes]
        ]


app = make_app(DeepRetroBackend())

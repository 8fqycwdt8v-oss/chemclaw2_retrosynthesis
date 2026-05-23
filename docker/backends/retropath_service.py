"""RetroPath RL service."""

from __future__ import annotations

from typing import Any

from _base import Backend, PlanRequest, make_app


class RetroPathBackend(Backend):
    name = "retropath"
    family = "biocatalysis"
    license = "MIT"
    citation = "Koch et al., bioRxiv 2019"
    url = "https://github.com/brsynth/RetroPathRL"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.runner = None

    def load(self) -> None:
        if self.runner is not None:
            return
        from retropath_rl.runner import RetroPathRunner  # type: ignore[import-not-found]
        self.runner = RetroPathRunner()

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        pathways = self.runner.plan(req.smiles, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": p["steps"],
                "leaves": p["leaves"],
                "in_stock_fraction": float(p.get("in_stock_fraction", 0.0)),
                "depth": len(p["steps"]),
                "final_score": float(p.get("score", 0.0)),
                "planner": "retropath",
            }
            for p in pathways[: req.top_k_routes]
        ]


app = make_app(RetroPathBackend())

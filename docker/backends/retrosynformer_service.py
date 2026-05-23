"""RetroSynFormer microservice."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class RetroSynFormerBackend(Backend):
    name = "retrosynformer"
    family = "planner"
    license = "Apache-2.0"
    citation = "Rydholm et al., RSC Digital Discovery 2026"
    url = "https://github.com/emmaryd/retrosynformer"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        sys.path.insert(0, "/opt/rsf")
        from retrosynformer.inference import load_pretrained  # type: ignore[import-not-found]
        self.model = load_pretrained("/weights/retrosynformer")

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        routes = self.model.plan(req.smiles, beam_size=req.top_k_routes, max_depth=req.max_depth)
        return [
            {
                "target": req.smiles,
                "steps": r["steps"],
                "leaves": r["leaves"],
                "in_stock_fraction": float(r.get("in_stock_fraction", 0.0)),
                "depth": len(r["steps"]),
                "final_score": float(r.get("score", 0.0)),
                "planner": "retrosynformer",
            }
            for r in routes
        ]


app = make_app(RetroSynFormerBackend())

"""RetroBioCat service."""

from __future__ import annotations

from typing import Any

from _base import Backend, PlanRequest, make_app


class RetroBioCatBackend(Backend):
    name = "retrobiocat"
    family = "biocatalysis"
    license = "MIT"
    citation = "Finnigan et al., Nat. Catal. 2021"
    url = "https://retrobiocat.com/"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.network = None

    def load(self) -> None:
        if self.network is not None:
            return
        from retrobiocat_web.retro.generation.network_generation.network import Network  # type: ignore[import-not-found]
        self.network = Network()

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        self.network.target = req.smiles
        self.network.generate_network(max_depth=req.max_depth)
        routes = self.network.get_pathways(max_paths=req.top_k_routes)
        return [
            {
                "target": req.smiles,
                "steps": [
                    {
                        "product": s["product"],
                        "reactants": s["reactants"],
                        "backend": "retrobiocat",
                        "score": float(s.get("score", 0.0)),
                    }
                    for s in r
                ],
                "leaves": [s["reactants"][-1] for s in r] if r else [],
                "in_stock_fraction": 0.0,
                "depth": len(r),
                "final_score": float(sum(s.get("score", 0.0) for s in r)),
                "planner": "retrobiocat",
            }
            for r in routes
        ]


app = make_app(RetroBioCatBackend())

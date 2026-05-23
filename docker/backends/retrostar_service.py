"""Retro* microservice."""

from __future__ import annotations

import sys
from typing import Any

from _base import Backend, PlanRequest, make_app


class RetroStarBackend(Backend):
    name = "retrostar"
    family = "planner"
    license = "MIT"
    citation = "Chen et al., ICML 2020"
    url = "https://github.com/binghong-ml/retro_star"
    capabilities = ["multi_step"]

    def __init__(self) -> None:
        self.planner = None

    def load(self) -> None:
        if self.planner is not None:
            return
        sys.path.insert(0, "/opt/retro_star")
        from retro_star.api import RSPlanner  # type: ignore[import-not-found]
        self.planner = RSPlanner(
            gpu=0, use_value_fn=True, iterations=100, expansion_topk=50
        )

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        result = self.planner.plan(req.smiles)
        if result is None:
            return []
        return [_walk(result, req.smiles)]


def _walk(tree: dict[str, Any], target: str) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    leaves: list[str] = []

    def visit(node: dict[str, Any]) -> None:
        kids = node.get("children", []) or []
        if not kids:
            leaves.append(node.get("smiles", ""))
            return
        steps.append(
            {
                "product": node.get("smiles"),
                "reactants": [k.get("smiles") for k in kids],
                "backend": "retrostar",
                "score": float(node.get("score", 0.0)),
            }
        )
        for k in kids:
            visit(k)

    visit(tree)
    return {
        "target": target,
        "steps": steps,
        "leaves": leaves,
        "in_stock_fraction": 1.0 if leaves else 0.0,
        "depth": len(steps),
        "final_score": float(tree.get("score", 0.0)),
        "planner": "retrostar",
    }


app = make_app(RetroStarBackend())

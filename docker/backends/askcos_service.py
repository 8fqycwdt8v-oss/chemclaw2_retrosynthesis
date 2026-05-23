"""ASKCOS microservice — wraps the upstream gRPC / Python API.

ASKCOS speaks its own RPC; the simplest portable wrapper is to point at
the in-container Python API (``makeit`` package)."""

from __future__ import annotations

from typing import Any

from _base import Backend, PlanRequest, make_app


class ASKCOSBackend(Backend):
    name = "askcos"
    family = "planner"
    license = "MIT"
    citation = "ASKCOS Consortium, Acc. Chem. Res. 2025"
    url = "https://github.com/ASKCOS"
    capabilities = ["single_step", "multi_step", "forward"]

    def __init__(self) -> None:
        self.retro = None
        self.tb = None

    def load(self) -> None:
        if self.retro is not None:
            return
        from makeit.retrosynthetic.transformer import RetroTransformer  # type: ignore[import-not-found]
        from makeit.synthetic.evaluation.template_based import TemplateBasedSynthesizer  # type: ignore[import-not-found]

        self.retro = RetroTransformer()
        self.retro.load()
        self.tb = TemplateBasedSynthesizer()
        self.tb.load()

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        hits = self.retro.get_outcomes(smiles, top_n=top_k)
        return [
            {
                "reactants": h["smiles_split"],
                "score": float(h.get("template_score", h.get("score", 0.0))),
                "rank": i,
                "template_id": str(h.get("tforms", [""])[0]) if h.get("tforms") else None,
            }
            for i, h in enumerate(hits[:top_k])
        ]

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        src = ".".join(reactants)
        out = self.tb.evaluate(src, top_n=top_k)
        return [{"smiles": o["outcome"]["smiles"], "score": float(o["score"])} for o in out[:top_k]]

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        from makeit.retrosynthetic.mcts.tree_builder import MCTS  # type: ignore[import-not-found]
        mcts = MCTS()
        result = mcts.get_buyable_paths(
            req.smiles, max_depth=req.max_depth, max_branching=25, expansion_time=60
        )
        return [_route_dict(r, req.smiles) for r in result.trees[: req.top_k_routes]]


def _route_dict(tree: Any, target: str) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    leaves: list[str] = []

    def walk(node: dict[str, Any]) -> None:
        kids = node.get("children", []) or []
        if not kids:
            leaves.append(node.get("smiles", ""))
            return
        for c in kids:
            steps.append(
                {
                    "product": node.get("smiles"),
                    "reactants": [g.get("smiles") for g in c.get("children", [])],
                    "backend": "askcos",
                    "score": float(c.get("plausibility", 0.0)),
                }
            )
            for g in c.get("children", []) or []:
                walk(g)

    walk(tree)
    return {
        "target": target,
        "steps": steps,
        "leaves": leaves,
        "in_stock_fraction": 1.0 if leaves else 0.0,
        "depth": len(steps),
        "final_score": float(tree.get("score", 0.0)),
        "planner": "askcos",
    }


app = make_app(ASKCOSBackend())

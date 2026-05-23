"""AiZynthFinder microservice — minimal FastAPI wrapper exposing the
uniform backend contract documented in ``backends/remote.py``.

This file is mounted into the aizynth Docker image; the gateway never
imports it directly.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="aizynth-backend", version="0.1.0")


class _PredictRequest(BaseModel):
    smiles: str
    top_k: int = 25


class _PlanRequest(BaseModel):
    smiles: str
    max_depth: int = 6
    stock: str = "zinc"
    top_k_routes: int = 5


_finder = None


def _load_finder() -> Any:
    global _finder
    if _finder is None:
        from aizynthfinder.aizynthfinder import AiZynthFinder  # type: ignore[import-not-found]

        cfg = os.environ.get("AIZYNTH_CONFIG", "/weights/aizynth/config.yml")
        _finder = AiZynthFinder(configfile=cfg)
        _finder.stock.select("zinc")
        _finder.expansion_policy.select("uspto")
    return _finder


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    return {"ok": True}


@app.get("/info")
def info() -> dict[str, Any]:
    return {
        "name": "aizynth",
        "family": "planner",
        "license": "MIT",
        "citation": "Genheden & Bjerrum, J. Cheminf. 2020",
        "capabilities": ["single_step", "multi_step"],
        "url": "https://github.com/MolecularAI/aizynthfinder",
        "enabled": True,
        "healthy": True,
    }


@app.post("/predict")
def predict(req: _PredictRequest) -> dict[str, Any]:
    finder = _load_finder()
    finder.target_smiles = req.smiles
    policy = finder.expansion_policy
    try:
        from aizynthfinder.chem.mol import TreeMolecule  # type: ignore[import-not-found]
    except Exception:
        return {"predictions": []}
    tm = TreeMolecule(parent=None, smiles=req.smiles)
    actions, priors = policy.get_actions([tm])
    out: list[dict[str, Any]] = []
    for rank, (action, prior) in enumerate(zip(actions[: req.top_k], priors[: req.top_k])):
        try:
            reactants = [m.smiles for m in action.apply()[0]]
        except Exception:
            continue
        out.append(
            {
                "reactants": reactants,
                "score": float(prior),
                "rank": rank,
                "template": getattr(action, "smarts", None),
                "template_id": getattr(action, "template_id", None),
            }
        )
    return {"predictions": out}


@app.post("/plan")
def plan(req: _PlanRequest) -> dict[str, Any]:
    finder = _load_finder()
    finder.target_smiles = req.smiles
    finder.config.search.max_depth = req.max_depth
    finder.tree_search()
    finder.build_routes()

    routes: list[dict[str, Any]] = []
    for r in finder.routes[: req.top_k_routes]:
        steps_data = []
        leaves = []
        for d in r.get("dict_with_extra", {}).get("children", []) or []:
            # Flatten; the gateway's Route schema accepts shallow info.
            steps_data.append(
                {
                    "product": d.get("smiles"),
                    "reactants": [c.get("smiles") for c in d.get("children", [])],
                    "backend": "aizynth",
                    "score": float(r.get("score", 0.0)),
                }
            )
            leaves.extend(c.get("smiles") for c in d.get("children", []))
        in_stock = float(r.get("in_stock", 0.0))
        routes.append(
            {
                "target": req.smiles,
                "steps": steps_data,
                "leaves": leaves,
                "in_stock_fraction": in_stock,
                "depth": len(steps_data),
                "final_score": float(r.get("score", 0.0)),
                "planner": "aizynth",
            }
        )
    return {"routes": routes}

"""Shared FastAPI skeleton for backend microservices.

Each per-backend service module subclasses :class:`Backend`, implements
``load`` (one-time model load) and ``predict`` (per-request inference),
and gets ``/predict`` ``/forward`` (optional) ``/info`` ``/healthz`` for
free via :func:`make_app`.

This file is copied into every backend image; it does **not** live in
the gateway's import path (gateway never imports ML deps directly).
"""

from __future__ import annotations

import logging
import os
import time
import traceback
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    smiles: str
    top_k: int = 25


class ForwardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reactants: list[str] = Field(..., min_length=1)
    top_k: int = 3


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    smiles: str
    max_depth: int = 6
    stock: str = "zinc"
    top_k_routes: int = 5


class Backend:
    name: str = "backend"
    family: str = "transformer"
    license: str = "MIT"
    citation: str | None = None
    url: str | None = None
    capabilities: list[str] = ["single_step"]

    def load(self) -> None:
        """One-time model load. Override per backend."""

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        """Return ``[{reactants, score, rank, template?, template_id?}, ...]``."""
        raise NotImplementedError

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        """Return ``[{smiles, score}, ...]``. Override if capability declared."""
        raise NotImplementedError

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        """Return a list of Route dicts. Override for multi-step planners."""
        raise NotImplementedError


def make_app(backend: Backend) -> FastAPI:
    app = FastAPI(title=f"chemclaw-backend-{backend.name}")
    state = {"ready": False, "loaded_at": None, "error": None}

    @app.on_event("startup")
    def _startup() -> None:
        if os.environ.get("LAZY_LOAD") == "1":
            return
        try:
            backend.load()
            state["ready"] = True
            state["loaded_at"] = time.time()
        except Exception as e:  # pragma: no cover
            state["error"] = str(e)
            log.exception("model load failed")

    def _ensure_loaded() -> None:
        if state["ready"]:
            return
        if state["error"]:
            raise HTTPException(503, f"model load failed: {state['error']}")
        try:
            backend.load()
            state["ready"] = True
        except Exception as e:
            state["error"] = str(e)
            log.exception("lazy model load failed")
            raise HTTPException(503, f"model load failed: {e}") from e

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"ok": True, "ready": state["ready"], "error": state["error"]}

    @app.get("/info")
    def info() -> dict[str, Any]:
        return {
            "name": backend.name,
            "family": backend.family,
            "license": backend.license,
            "citation": backend.citation,
            "url": backend.url,
            "capabilities": backend.capabilities,
            "enabled": True,
            "healthy": state["ready"],
        }

    @app.post("/predict")
    def predict(req: PredictRequest) -> dict[str, Any]:
        _ensure_loaded()
        try:
            preds = backend.predict(req.smiles, req.top_k)
        except NotImplementedError:
            raise HTTPException(400, "single_step not supported by this backend") from None
        except Exception as e:
            log.exception("predict failed")
            raise HTTPException(500, f"{e!r}\n{traceback.format_exc()}") from e
        return {"predictions": preds}

    @app.post("/forward")
    def forward(req: ForwardRequest) -> dict[str, Any]:
        _ensure_loaded()
        try:
            products = backend.forward(req.reactants, req.top_k)
        except NotImplementedError:
            raise HTTPException(400, "forward not supported by this backend") from None
        except Exception as e:
            log.exception("forward failed")
            raise HTTPException(500, repr(e)) from e
        return {"products": products}

    @app.post("/plan")
    def plan(req: PlanRequest) -> dict[str, Any]:
        _ensure_loaded()
        try:
            routes = backend.plan(req)
        except NotImplementedError:
            raise HTTPException(400, "multi_step not supported by this backend") from None
        except Exception as e:
            log.exception("plan failed")
            raise HTTPException(500, repr(e)) from e
        return {"routes": routes}

    return app

"""Shared FastAPI skeleton for backend microservices.

Each per-backend service module subclasses :class:`Backend`,
implements ``load`` and whichever of ``predict`` / ``forward`` / ``plan``
matches its advertised ``capabilities``, then calls :func:`make_app`.

Routes are registered based on capability — a backend that doesn't
advertise ``forward`` simply doesn't expose ``POST /forward`` and the
container returns ``404 Not Found`` rather than ``400`` for that path.
Capability and method overrides therefore cannot drift out of sync.

This file is copied into every backend image; it does **not** live in
the gateway's import path (gateway never imports ML deps directly).
"""

from __future__ import annotations

import logging
import os
import time
import traceback
from collections.abc import Callable
from contextlib import asynccontextmanager
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
    """Base class. Override the methods whose capabilities you declare."""

    name: str = "backend"
    family: str = "transformer"
    license: str = "MIT"
    citation: str | None = None
    url: str | None = None
    capabilities: list[str] = ["single_step"]

    def load(self) -> None:
        """One-time model load. Override per backend."""

    # The signatures below exist only as type hints. Whether they are
    # *implemented* is detected by checking whether the subclass
    # overrides them; absent overrides simply don't get a route.

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    def plan(self, req: PlanRequest) -> list[dict[str, Any]]:
        raise NotImplementedError


def _try_loaders(
    candidates: list[tuple[str, Callable[[], Any]]],
    *,
    pin_env: str | None = None,
    label: str = "model",
) -> Any:
    """Try named loader strategies in order, optionally pinned by an
    env variable, and raise a uniform error message accumulating each
    failure. Used by backends whose upstream loader API drifts between
    releases (MEGAN, RetroChimera, ...).
    """
    pinned = os.environ.get(pin_env) if pin_env else None
    if pinned:
        candidates = [(n, fn) for n, fn in candidates if n == pinned]
        if not candidates:
            raise RuntimeError(f"{pin_env}={pinned} did not match any known loader for {label}")

    errors: list[str] = []
    for name, fn in candidates:
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e!r}")
    raise RuntimeError(
        f"{label} load failed for every known upstream entry point. "
        + (f"Set {pin_env}={{{','.join(n for n, _ in candidates)}}} to pin one. " if pin_env else "")
        + "Tried: "
        + "; ".join(errors)
    )


def make_app(backend: Backend) -> FastAPI:
    """Build a FastAPI app exposing only the endpoints that ``backend``
    advertises in ``capabilities``. Lifespan handler does the one-time
    model load (skip with ``LAZY_LOAD=1``).
    """
    state: dict[str, Any] = {"ready": False, "loaded_at": None, "error": None}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if os.environ.get("LAZY_LOAD") != "1":
            try:
                backend.load()
                state["ready"] = True
                state["loaded_at"] = time.time()
            except Exception as e:  # pragma: no cover
                state["error"] = str(e)
                log.exception("model load failed")
        yield

    app = FastAPI(title=f"chemclaw-backend-{backend.name}", lifespan=lifespan)

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

    # Register only the routes the backend advertises. Unsupported
    # capabilities become natural 404s rather than 400s.
    caps = set(backend.capabilities)

    if "single_step" in caps:

        @app.post("/predict")
        def predict(req: PredictRequest) -> dict[str, Any]:
            _ensure_loaded()
            try:
                preds = backend.predict(req.smiles, req.top_k)
            except Exception as e:
                log.exception("predict failed")
                raise HTTPException(500, f"{e!r}\n{traceback.format_exc()}") from e
            return {"predictions": preds}

    if "forward" in caps:

        @app.post("/forward")
        def forward(req: ForwardRequest) -> dict[str, Any]:
            _ensure_loaded()
            try:
                products = backend.forward(req.reactants, req.top_k)
            except Exception as e:
                log.exception("forward failed")
                raise HTTPException(500, repr(e)) from e
            return {"products": products}

    if "multi_step" in caps:

        @app.post("/plan")
        def plan(req: PlanRequest) -> dict[str, Any]:
            _ensure_loaded()
            try:
                routes = backend.plan(req)
            except Exception as e:
                log.exception("plan failed")
                raise HTTPException(500, repr(e)) from e
            return {"routes": routes}

    return app

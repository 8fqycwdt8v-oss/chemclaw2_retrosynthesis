"""Uniform contract every retrosynthesis backend speaks to the gateway.

Two flavours:

* :class:`SingleStepBackend` — proposes reactant sets for one product.
* :class:`MultiStepPlanner` — produces full routes back to stock molecules.

Both flavours expose ``info()`` / ``healthz()``. Concrete adapters live in
``adapters/``; many of them just call a remote microservice via
:class:`chemclaw_retro.backends.remote.RemoteBackend`.
"""

from __future__ import annotations

import abc

from ..schemas import (
    BackendInfo,
    ForwardProduct,
    ForwardRequest,
    SinglePrediction,
)


class SingleStepBackend(abc.ABC):
    """Abstract single-step retrosynthesis backend."""

    name: str

    @abc.abstractmethod
    async def info(self) -> BackendInfo: ...

    @abc.abstractmethod
    async def healthz(self) -> bool: ...

    @abc.abstractmethod
    async def predict(self, smiles: str, top_k: int = 25) -> list[SinglePrediction]:
        """Return up to ``top_k`` reactant proposals for ``smiles``."""


class ForwardBackend(abc.ABC):
    """Forward synthesis backend used for round-trip validation."""

    name: str

    @abc.abstractmethod
    async def forward(self, req: ForwardRequest) -> list[ForwardProduct]: ...


class MultiStepPlanner(abc.ABC):
    """Abstract multi-step retrosynthetic planner.

    The public ``plan(...)`` signature takes the same four fields the
    backend's ``/plan`` endpoint accepts: ``smiles`` plus the search
    knobs. Gateway-only fields (e.g. which planner to pick) are
    consumed by the route, not forwarded.
    """

    name: str

    @abc.abstractmethod
    async def info(self) -> BackendInfo: ...

    @abc.abstractmethod
    async def plan(
        self,
        smiles: str,
        *,
        max_depth: int = 6,
        stock: str = "zinc",
        top_k_routes: int = 5,
    ) -> list[dict]:
        """Return a list of Route dicts (validated by the route)."""


class BackendError(RuntimeError):
    """Wraps any failure from a remote backend so the aggregator can report
    a 'degraded' result instead of failing the whole call."""

    def __init__(self, backend: str, message: str, *, cause: Exception | None = None):
        super().__init__(f"[{backend}] {message}")
        self.backend = backend
        self.cause = cause

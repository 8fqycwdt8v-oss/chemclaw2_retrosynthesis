"""HTTP client shared by every adapter that talks to a remote microservice.

Each backend container exposes:

    POST /predict      {smiles, top_k}        → {predictions: [...]}
    POST /forward      {reactants, top_k}     → {products: [...]}     (optional)
    GET  /info                                → BackendInfo
    GET  /healthz                             → {ok: true}
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..schemas import (
    BackendInfo,
    ForwardProduct,
    ForwardRequest,
    SinglePrediction,
)
from .base import BackendError, ForwardBackend, SingleStepBackend


class RemoteBackend(SingleStepBackend, ForwardBackend):
    """Single class covers both single-step prediction and forward synthesis;
    forward is only exercised by backends that advertise the capability."""

    def __init__(
        self,
        name: str,
        url: str,
        *,
        timeout_s: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.name = name
        self.url = url.rstrip("/")
        self.timeout_s = timeout_s
        self._client = client

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        client = self._client or httpx.AsyncClient(timeout=self.timeout_s)
        owns = self._client is None
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=0.5, max=4),
                retry=retry_if_exception_type((httpx.TransportError,)),
                reraise=True,
            ):
                with attempt:
                    resp = await client.request(
                        method, f"{self.url}{path}", timeout=self.timeout_s, **kwargs
                    )
            resp.raise_for_status()
            return resp
        except httpx.HTTPError as e:
            raise BackendError(self.name, f"{method} {path} failed: {e}", cause=e) from e
        finally:
            if owns:
                await client.aclose()

    async def info(self) -> BackendInfo:
        resp = await self._request("GET", "/info")
        return BackendInfo.model_validate(resp.json())

    async def healthz(self) -> bool:
        try:
            resp = await self._request("GET", "/healthz")
            return bool(resp.json().get("ok"))
        except BackendError:
            return False

    async def predict(self, smiles: str, top_k: int = 25) -> list[SinglePrediction]:
        resp = await self._request("POST", "/predict", json={"smiles": smiles, "top_k": top_k})
        data = resp.json().get("predictions", [])
        return [SinglePrediction.model_validate(p) for p in data]

    async def forward(self, req: ForwardRequest) -> list[ForwardProduct]:
        resp = await self._request("POST", "/forward", json=req.model_dump())
        data = resp.json().get("products", [])
        return [ForwardProduct.model_validate(p) for p in data]

    async def plan(
        self,
        smiles: str,
        *,
        max_depth: int = 6,
        stock: str = "zinc",
        top_k_routes: int = 5,
    ) -> list[dict[str, Any]]:
        """POST /plan with exactly the fields the shared backend
        ``PlanRequest`` accepts (extra='forbid'). Gateway-only knobs like
        ``planner`` must be stripped here, not forwarded.
        """
        body = {
            "smiles": smiles,
            "max_depth": max_depth,
            "stock": stock,
            "top_k_routes": top_k_routes,
        }
        resp = await self._request("POST", "/plan", json=body)
        return list(resp.json().get("routes", []))

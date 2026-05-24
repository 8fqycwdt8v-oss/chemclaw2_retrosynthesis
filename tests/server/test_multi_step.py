"""Regression: /retrosynthesis/multi_step must

1. accept any catalogue planner name (not be limited to a closed Literal),
2. strip the gateway-only `planner` field from the body sent to the
   backend's /plan endpoint (whose PlanRequest uses extra='forbid'),
3. fail clearly when the requested planner does not advertise multi_step.
"""

from __future__ import annotations

import pytest


def test_plan_strips_planner_field() -> None:
    """RemoteBackend.plan must only forward the four backend-PlanRequest
    fields (smiles, max_depth, stock, top_k_routes), never the gateway-only
    'planner' selector."""
    from chemclaw_retro.backends.remote import RemoteBackend

    captured: dict = {}

    class _StubBackend(RemoteBackend):
        async def _request(self, method, path, **kwargs):  # type: ignore[override]
            captured["method"] = method
            captured["path"] = path
            captured["json"] = kwargs.get("json")

            class _R:
                @staticmethod
                def json() -> dict:
                    return {"routes": []}

            return _R()  # type: ignore[return-value]

    import asyncio

    asyncio.run(
        _StubBackend("syntheseus", "http://x:9000").plan(
            "CCO", max_depth=4, stock="zinc", top_k_routes=3
        )
    )
    assert captured["path"] == "/plan"
    assert set(captured["json"].keys()) == {"smiles", "max_depth", "stock", "top_k_routes"}
    assert "planner" not in captured["json"]


def test_multistep_request_accepts_any_planner_name() -> None:
    """Pydantic must not reject Phase 2-4 planner names anymore."""
    from chemclaw_retro.schemas import MultiStepRequest

    # Previously rejected by the Literal:
    req = MultiStepRequest(smiles="CCO", planner="retrostar")
    assert req.planner == "retrostar"
    req2 = MultiStepRequest(smiles="CCO", planner="deepretro")
    assert req2.planner == "deepretro"


def test_resolve_planner_rejects_non_multi_step() -> None:
    from fastapi import HTTPException

    from chemclaw_retro.server.routes.multi_step import _resolve_planner

    # retrosim is similarity-family, single-step only → must be rejected.
    with pytest.raises(HTTPException) as exc:
        _resolve_planner("retrosim", {"retrosim": object()})
    assert exc.value.status_code == 400
    assert "multi_step" in exc.value.detail

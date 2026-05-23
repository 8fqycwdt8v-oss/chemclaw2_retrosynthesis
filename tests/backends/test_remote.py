"""Verify the uniform HTTP contract via a mocked transport."""

from __future__ import annotations

import httpx
import pytest

from chemclaw_retro.backends.remote import RemoteBackend


@pytest.mark.asyncio
async def test_predict_round_trips_schema():
    body = {
        "predictions": [
            {"reactants": ["CCO", "CC(=O)Cl"], "score": 0.9, "rank": 0},
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/predict"
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://backend") as c:
        b = RemoteBackend("backend", "http://backend", client=c)
        preds = await b.predict("CC(=O)OCC", top_k=3)
    assert len(preds) == 1
    assert preds[0].reactants == ["CCO", "CC(=O)Cl"]


@pytest.mark.asyncio
async def test_healthz_falls_to_false_on_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://backend") as c:
        b = RemoteBackend("backend", "http://backend", client=c)
        assert await b.healthz() is False

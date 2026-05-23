"""Smoke tests against the FastAPI app, with all backends mocked."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import chemclaw_retro.backends.registry as registry
from chemclaw_retro.backends.base import SingleStepBackend
from chemclaw_retro.schemas import BackendInfo, SinglePrediction


class _FakeBackend(SingleStepBackend):
    def __init__(self, name: str, preds: list[SinglePrediction]):
        self.name = name
        self._preds = preds

    async def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name, family="template", license="MIT", capabilities=["single_step"]
        )

    async def healthz(self) -> bool:
        return True

    async def predict(self, smiles: str, top_k: int = 25) -> list[SinglePrediction]:
        return self._preds[:top_k]


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    pytest.importorskip("rdkit")
    pytest.importorskip("fastapi")

    fake_a = _FakeBackend(
        "a",
        [SinglePrediction(reactants=["CCO", "CC(=O)Cl"], score=0.9, rank=0)],
    )
    fake_b = _FakeBackend(
        "b",
        [SinglePrediction(reactants=["CC(=O)Cl", "CCO"], score=0.6, rank=0)],
    )
    monkeypatch.setattr(registry, "all_backends", lambda: {"a": fake_a, "b": fake_b})
    registry.reset_registry_cache()

    from chemclaw_retro.server.app import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c


def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_backends_list(client: TestClient) -> None:
    r = client.get("/backends")
    assert r.status_code == 200
    names = sorted(b["name"] for b in r.json())
    assert names == ["a", "b"]


def test_single_step_aggregates_two_backends(client: TestClient) -> None:
    r = client.post(
        "/retrosynthesis/single_step",
        json={
            "smiles": "CC(=O)OCC",
            "top_k": 5,
            "backends": "auto",
            "return_provenance": True,
            "run_round_trip": False,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["degraded"] is False
    assert len(body["results"]) == 1
    top = body["results"][0]
    assert top["consensus_count"] == 2
    assert {c["backend"] for c in top["provenance"]} == {"a", "b"}

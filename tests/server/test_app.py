"""Smoke tests against the FastAPI app, with all backends mocked."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from chemclaw_retro.schemas import SinglePrediction


@pytest.fixture()
def client(
    make_fake_backend: Callable,
    registry_with: Callable,
) -> Iterator[TestClient]:
    pytest.importorskip("rdkit")
    pytest.importorskip("fastapi")

    fake_a = make_fake_backend(
        "a", [SinglePrediction(reactants=["CCO", "CC(=O)Cl"], score=0.9, rank=0)]
    )
    fake_b = make_fake_backend(
        "b", [SinglePrediction(reactants=["CC(=O)Cl", "CCO"], score=0.6, rank=0)]
    )
    registry_with({"a": fake_a, "b": fake_b})

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
    body = r.json()
    by_name = {b["name"]: b for b in body}

    # Enabled (fake) backends reflect live state.
    assert by_name["a"]["enabled"] is True
    assert by_name["a"]["healthy"] is True
    assert by_name["b"]["enabled"] is True

    # Catalogue entries that aren't enabled show up with enabled=false
    # so clients can see the full menu + per-backend license.
    assert "askcos" in by_name
    assert by_name["askcos"]["enabled"] is False
    assert by_name["askcos"]["healthy"] is False
    assert by_name["askcos"]["license"] == "MIT"


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

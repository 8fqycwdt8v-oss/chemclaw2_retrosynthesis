"""Regression: scoring loaders must retry after a TTL when the optional
dep / weights are missing, rather than permanently caching False on
first failure (which previously broke recovery after a late mount or
pip install)."""

from __future__ import annotations

import pytest

from chemclaw_retro.scoring import rascore, scscore


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch) -> None:
    rascore._scorer = None
    rascore._last_failure_at = 0.0
    scscore._model = None
    scscore._last_failure_at = 0.0


def test_rascore_retries_after_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    # First load fails (no rascore package installed).
    assert rascore._load() is None
    # Permanently caching None? Within the TTL window, yes:
    assert rascore._load() is None
    # Past the TTL, it MUST re-attempt — fake the clock.
    monkeypatch.setattr(
        rascore.time, "monotonic", lambda: rascore._last_failure_at + rascore._RETRY_INTERVAL_S + 1
    )
    calls: list[int] = []

    def fake_import(*a, **kw):
        calls.append(1)
        raise ImportError("still missing")

    monkeypatch.setattr("builtins.__import__", fake_import)
    rascore._load()
    assert calls, "expected _load() to retry after the TTL"


def test_scscore_retries_after_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    assert scscore._load() is None
    assert scscore._load() is None
    monkeypatch.setattr(
        scscore.time, "monotonic", lambda: scscore._last_failure_at + scscore._RETRY_INTERVAL_S + 1
    )
    calls: list[int] = []

    def fake_import(*a, **kw):
        calls.append(1)
        raise ImportError("still missing")

    monkeypatch.setattr("builtins.__import__", fake_import)
    scscore._load()
    assert calls, "expected _load() to retry after the TTL"

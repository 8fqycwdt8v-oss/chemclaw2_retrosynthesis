"""Regression: scoring loaders must retry after a TTL when the optional
dep / weights are missing, rather than permanently caching False on
first failure (which previously broke recovery after a late mount or
pip install)."""

from __future__ import annotations

import time

import pytest

from chemclaw_retro._lazy import TTLLoader


def test_loader_returns_none_within_retry_window() -> None:
    attempts: list[int] = []

    def factory() -> object:
        attempts.append(1)
        raise ImportError("still missing")

    loader: TTLLoader[object] = TTLLoader(factory, retry_s=60.0)
    assert loader.get() is None
    assert loader.get() is None  # within window: no retry
    assert len(attempts) == 1


def test_loader_retries_after_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    def factory() -> object:
        attempts.append(1)
        raise ImportError("still missing")

    loader: TTLLoader[object] = TTLLoader(factory, retry_s=60.0)
    assert loader.get() is None
    monkeypatch.setattr(time, "monotonic", lambda: loader._last_failure_at + 61.0)
    loader.get()
    assert len(attempts) == 2, "expected the loader to retry after the TTL"


def test_loader_caches_success() -> None:
    attempts: list[int] = []

    def factory() -> object:
        attempts.append(1)
        return object()

    loader: TTLLoader[object] = TTLLoader(factory)
    a = loader.get()
    b = loader.get()
    assert a is b
    assert len(attempts) == 1


def test_scoring_modules_use_ttl_loader() -> None:
    """Smoke: the new helper is wired into rascore + scscore + rxnfp."""
    from chemclaw_retro.classify import rxnfp
    from chemclaw_retro.scoring import rascore, scscore

    assert isinstance(rascore._LOADER, TTLLoader)
    assert isinstance(scscore._LOADER, TTLLoader)
    assert isinstance(rxnfp._LOADER, TTLLoader)

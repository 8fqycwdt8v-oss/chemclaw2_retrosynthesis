"""Regression: select_backends must reject bare-string non-'auto' input
instead of iterating it character-by-character (which previously
produced misleading 'unknown backend' errors for each letter)."""

from __future__ import annotations

import pytest

import chemclaw_retro.backends.registry as registry


def test_bare_string_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry, "all_backends", lambda: {"aizynth": object()})
    registry.reset_registry_cache()
    with pytest.raises(ValueError, match="bare string"):
        registry.select_backends("aizynth")


def test_auto_string_works(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    monkeypatch.setattr(registry, "all_backends", lambda: {"aizynth": sentinel})
    registry.reset_registry_cache()
    assert registry.select_backends("auto") == [sentinel]


def test_list_works(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    monkeypatch.setattr(registry, "all_backends", lambda: {"aizynth": sentinel})
    registry.reset_registry_cache()
    assert registry.select_backends(["aizynth"]) == [sentinel]

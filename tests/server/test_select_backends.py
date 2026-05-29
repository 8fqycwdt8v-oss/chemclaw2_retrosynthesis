"""Regression: select_backends must reject bare-string non-'auto' input
instead of iterating it character-by-character (which previously
produced misleading 'unknown backend' errors for each letter)."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from chemclaw_retro.backends import registry


def test_bare_string_rejected(registry_with: Callable) -> None:
    registry_with({"aizynth": object()})
    with pytest.raises(ValueError, match="bare string"):
        registry.select_backends("aizynth")


def test_auto_string_works(registry_with: Callable) -> None:
    sentinel = object()
    registry_with({"aizynth": sentinel})
    assert registry.select_backends("auto") == [sentinel]


def test_list_works(registry_with: Callable) -> None:
    sentinel = object()
    registry_with({"aizynth": sentinel})
    assert registry.select_backends(["aizynth"]) == [sentinel]

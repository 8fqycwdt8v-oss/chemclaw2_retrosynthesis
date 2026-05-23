"""Every adapter exposes a non-empty BackendInfo with a permissive
license — that's the bar for inclusion in this repo."""

from __future__ import annotations

import pytest

from chemclaw_retro.backends.adapters._catalogue import CATALOGUE

PERMISSIVE = {"MIT", "Apache-2.0", "BSD", "BSD-3-Clause"}


def test_catalogue_non_empty():
    assert len(CATALOGUE) >= 30, "expected ≥30 backends in the catalogue"


@pytest.mark.parametrize("name", list(CATALOGUE.keys()))
def test_adapter_has_permissive_license(name: str):
    info = CATALOGUE[name]
    assert info.name == name
    assert info.license in PERMISSIVE, f"{name} has non-permissive license {info.license!r}"
    assert info.family in {
        "template",
        "transformer",
        "graph",
        "similarity",
        "llm",
        "hybrid",
        "planner",
        "biocatalysis",
        "scoring",
        "classification",
        "conditions",
        "forward",
    }
    assert info.capabilities, f"{name} declares no capabilities"


def test_catalogue_names_are_unique():
    assert len(CATALOGUE) == len({i.name for i in CATALOGUE.values()})

"""Central catalogue of every adapter's ``BackendInfo`` so the
``/backends`` endpoint can surface license / family / citation metadata
even when the remote container is unhealthy.

Adapter modules in this package each define ``INFO = BackendInfo(...)``.
We discover them at import time via :mod:`pkgutil` so adding a new
backend is a one-file change (drop a new ``<name>.py`` next to this
module) instead of a coordinated edit to two parallel lists here.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from ...schemas import BackendInfo

_PACKAGE = __name__.rsplit(".", 1)[0]
_PACKAGE_DIR = str(Path(__file__).resolve().parent)


def _discover() -> dict[str, BackendInfo]:
    out: dict[str, BackendInfo] = {}
    for mod_info in pkgutil.iter_modules([_PACKAGE_DIR]):
        if mod_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{_PACKAGE}.{mod_info.name}")
        info = getattr(module, "INFO", None)
        if isinstance(info, BackendInfo):
            out[info.name] = info
    return out


CATALOGUE: dict[str, BackendInfo] = _discover()


def get_info(name: str) -> BackendInfo | None:
    return CATALOGUE.get(name)


def all_known_backends() -> list[BackendInfo]:
    return list(CATALOGUE.values())

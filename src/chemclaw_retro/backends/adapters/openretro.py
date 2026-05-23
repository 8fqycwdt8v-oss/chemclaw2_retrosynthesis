"""OpenRetro — Coley group's Docker-based benchmarking framework wrapping
GLN, NeuralSym, RetroXpert, Transformer."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="openretro",
    family="planner",
    license="MIT",
    citation="Coley group, OpenRetro README",
    capabilities=["single_step"],
    url="https://github.com/coleygroup/openretro",
)

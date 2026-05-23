"""Retro* — neural-guided A* search with learned value network."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retrostar",
    family="planner",
    license="MIT",
    citation="Chen et al., ICML 2020",
    capabilities=["multi_step"],
    url="https://github.com/binghong-ml/retro_star",
)

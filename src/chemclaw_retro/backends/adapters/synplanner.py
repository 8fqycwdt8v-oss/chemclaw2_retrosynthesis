"""SynPlanner — MCTS + GNN policy/value retrosynthetic planner."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="synplanner",
    family="planner",
    license="MIT",
    citation="Tagirov et al., JCIM 2025",
    capabilities=["multi_step"],
    url="https://github.com/Laboratoire-de-Chemoinformatique/SynPlanner",
)

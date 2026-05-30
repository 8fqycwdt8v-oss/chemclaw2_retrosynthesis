"""SynPlanner — MCTS + GNN policy/value retrosynthetic planner."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="synplanner",
    family="planner",
    license="MIT",
    citation="Tagirov et al., JCIM 2025",
    capabilities=["multi_step"],
    url="https://github.com/Laboratoire-de-Chemoinformatique/SynPlanner",
    deploy=BackendDeploy(
        dockerfile="docker/backends/synplanner.Dockerfile",
        service="synplanner",
        host_port=9042,
        profiles=["phase3", "planner"],
        gpu=True,
    ),
)

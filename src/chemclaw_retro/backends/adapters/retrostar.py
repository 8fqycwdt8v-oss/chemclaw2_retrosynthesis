"""Retro* — neural-guided A* search with learned value network."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrostar",
    family="planner",
    license="MIT",
    citation="Chen et al., ICML 2020",
    capabilities=["multi_step"],
    url="https://github.com/binghong-ml/retro_star",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retrostar.Dockerfile",
        service="retrostar",
        host_port=9044,
        profiles=["phase3", "planner"],
        gpu=True,
    ),
)

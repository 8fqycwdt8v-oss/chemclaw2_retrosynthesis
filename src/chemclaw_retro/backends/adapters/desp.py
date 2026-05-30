"""DESP — Double-Ended Synthesis Planning (Coley group, NeurIPS 2024).

Bidirectional search bound by a goal constraint; benchmarks on
pistachio_reachable / pistachio_hard / uspto_190."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="desp",
    family="planner",
    license="MIT",
    citation="Yu et al., NeurIPS 2024",
    capabilities=["multi_step"],
    url="https://github.com/coleygroup/desp",
    deploy=BackendDeploy(
        dockerfile="docker/backends/desp.Dockerfile",
        service="desp",
        host_port=9045,
        profiles=["phase3", "planner"],
        gpu=True,
    ),
)

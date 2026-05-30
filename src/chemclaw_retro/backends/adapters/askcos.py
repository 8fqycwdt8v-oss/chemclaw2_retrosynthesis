"""ASKCOS — MIT's open-source synthesis-planning suite.

Bundles four single-step models (Template, Transformer, Graph2SMILES,
Retrosim) plus an MCTS planner. The container exposes both
``/predict`` (single-step) and ``/plan`` (multi-step) so the gateway can
use it as both a single-step backend and a planner.
"""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="askcos",
    family="planner",
    license="MIT",
    citation="ASKCOS Consortium, Acc. Chem. Res. 2025",
    capabilities=["single_step", "multi_step", "forward"],
    url="https://github.com/ASKCOS",
    deploy=BackendDeploy(
        dockerfile="docker/backends/askcos.Dockerfile",
        service="askcos",
        host_port=9040,
        profiles=["phase3", "planner"],
        gpu=True,
    ),
)

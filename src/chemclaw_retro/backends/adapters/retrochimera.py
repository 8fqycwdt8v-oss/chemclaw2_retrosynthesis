"""RetroChimera — Microsoft + Novartis ensemble (NeuralLoc + R-SMILES 2
+ learned reranker). Already an ensemble in its own right; we keep it
as one backend and let our outer aggregator combine its output with the
other backends'."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retrochimera",
    family="hybrid",
    license="MIT",
    citation="Maziarz et al., arXiv:2412.05269 (Microsoft + Novartis, 2024)",
    capabilities=["single_step", "multi_step"],
    url="https://github.com/microsoft/retrochimera",
    deploy=BackendDeploy(
        dockerfile="docker/backends/retrochimera.Dockerfile",
        service="retrochimera",
        host_port=9047,
        profiles=["phase3", "planner"],
        gpu=True,
    ),
)

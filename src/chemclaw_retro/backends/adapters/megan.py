"""MEGAN — Molecule Edit Graph Attention Network (Molecule.one).

Trained on USPTO-50K (template-free, graph-edit sequence). Weights ship
as ``megan_data.zip`` on the v1.1 GitHub release."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="megan",
    family="graph",
    license="MIT",
    citation="Sacha et al., JCIM 2021",
    capabilities=["single_step"],
    url="https://github.com/molecule-one/megan",
    deploy=BackendDeploy(
        dockerfile="docker/backends/megan.Dockerfile",
        service="megan",
        host_port=9031,
        profiles=["phase2", "graph"],
        gpu=True,
    ),
)

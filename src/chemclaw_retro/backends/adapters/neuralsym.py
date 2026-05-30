"""NeuralSym — reimplementation of Segler & Waller's template relevance
network (linminhtoo)."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="neuralsym",
    family="template",
    license="MIT",
    citation="Segler & Waller, Chem. Eur. J. 2017 (reimpl. by Lin)",
    capabilities=["single_step"],
    url="https://github.com/linminhtoo/neuralsym",
    deploy=BackendDeploy(
        dockerfile="docker/backends/neuralsym.Dockerfile",
        service="neuralsym",
        host_port=9012,
        profiles=["phase2", "template"],
        gpu=True,
    ),
)

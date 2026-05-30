"""Graph2SMILES — permutation-invariant graph-to-sequence transformer
(Coley group). Checkpoints for USPTO_50k, USPTO_full, USPTO_480k, and
USPTO_STEREO are on Google Drive; pull them with
``scripts/download_weights.sh graph2smiles``."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="graph2smiles",
    family="graph",
    license="MIT",
    citation="Tu & Coley, JCIM 2022",
    capabilities=["single_step", "forward"],
    url="https://github.com/coleygroup/Graph2SMILES",
    deploy=BackendDeploy(
        dockerfile="docker/backends/graph2smiles.Dockerfile",
        service="graph2smiles",
        host_port=9030,
        profiles=["phase2", "graph"],
        gpu=True,
    ),
)

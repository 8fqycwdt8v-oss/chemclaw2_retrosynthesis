"""G2Retro — two-step graph generative model. ``g2retro_ens`` is the
authors' own ensemble variant; we expose both as separate backends so
our outer aggregator sees their diversity."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="g2retro",
    family="graph",
    license="MIT",
    citation="Chen & Zhang, Nat. Commun. 2023",
    capabilities=["single_step"],
    url="https://github.com/yhwwang/G2Retro",
    deploy=BackendDeploy(
        dockerfile="docker/backends/g2retro.Dockerfile",
        service="g2retro",
        host_port=9035,
        profiles=["phase2", "graph"],
        gpu=True,
    ),
)

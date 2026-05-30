"""Disconnection-aware Chemformer (rxn4chemistry).

Same backbone as Chemformer but conditioned on a tagged bond to break,
yielding more diverse / chemist-intuitive disconnections."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="disconnection_chemformer",
    family="transformer",
    license="MIT",
    citation="Thakkar et al., Chem. Sci. 2023",
    capabilities=["single_step"],
    url="https://github.com/rxn4chemistry/disconnection_aware_retrosynthesis",
    deploy=BackendDeploy(
        dockerfile="docker/backends/disconnection_chemformer.Dockerfile",
        service="disc-chemformer",
        host_port=9025,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)

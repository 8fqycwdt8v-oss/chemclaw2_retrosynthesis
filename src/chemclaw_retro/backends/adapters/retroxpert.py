"""RetroXpert — NMT-based retrosynthesis (UTA SMILE).

WARNING: the authors disclosed an information-leak in the original code
that inflated reported metrics. We expose this backend with
``compromised=True`` in the BackendInfo extras so consumers can choose
to exclude it from the aggregator until the leak-fix branch is wired
in."""

from __future__ import annotations

from ...schemas import BackendDeploy, BackendInfo

INFO = BackendInfo(
    name="retroxpert",
    family="transformer",
    license="MIT",
    citation="Yan et al., NeurIPS 2020 (FLAG: information-leak disclosed)",
    capabilities=["single_step"],
    url="https://github.com/uta-smile/RetroXpert",
    enabled=False,  # opt-in only until leak-fix branch lands,
    deploy=BackendDeploy(
        dockerfile="docker/backends/retroxpert.Dockerfile",
        service="retroxpert",
        host_port=9029,
        profiles=["phase2", "transformer"],
        gpu=True,
    ),
)

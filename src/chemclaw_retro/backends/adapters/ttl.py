"""Triple Transformer Loop (TTL) multi-step retrosynthesis with
disconnection awareness (Reymond Group)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="ttl",
    family="planner",
    license="MIT",
    citation="Andronov et al., Chem. Sci. 2023",
    capabilities=["multi_step"],
    url="https://github.com/reymond-group/MultiStepRetrosynthesisTTL",
)

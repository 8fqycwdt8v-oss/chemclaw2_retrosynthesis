"""RetroBridge — Markov bridge model for template-free retrosynthesis
(Igashov et al., ICLR 2024)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retrobridge",
    family="graph",
    license="MIT",
    citation="Igashov et al., ICLR 2024",
    capabilities=["single_step"],
    url="https://github.com/igashov/RetroBridge",
)

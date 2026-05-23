"""RetroDFM-R — reasoning LLM for retrosynthesis (currently SoTA on
USPTO-50K with 65% top-1 as of mid-2025)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retrodfm",
    family="llm",
    license="Apache-2.0",
    citation="arXiv:2507.17448",
    capabilities=["single_step"],
    url="https://arxiv.org/abs/2507.17448",
)

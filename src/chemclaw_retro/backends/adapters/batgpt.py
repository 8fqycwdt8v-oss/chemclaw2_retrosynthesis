"""BatGPT-Chem — 15B-param chemistry foundation LLM."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="batgpt",
    family="llm",
    license="Apache-2.0",
    citation="Liu et al., arXiv:2408.10285",
    capabilities=["single_step"],
    url="https://arxiv.org/abs/2408.10285",
)

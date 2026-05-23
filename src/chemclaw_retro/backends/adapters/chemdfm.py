"""ChemDFM-13B — chemistry foundation LLM (HuggingFace)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="chemdfm",
    family="llm",
    license="Apache-2.0",
    citation="Zhao et al., arXiv:2401.14818",
    capabilities=["single_step"],
    url="https://huggingface.co/OpenDFM/ChemDFM-13B-v1.0",
)

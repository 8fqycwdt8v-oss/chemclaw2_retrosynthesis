"""RSGPT — generative transformer pretrained on ~10B template-generated
reactions. Weights on Zenodo (10.5281/zenodo.15336192)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="rsgpt",
    family="llm",
    license="MIT",
    citation="Liu et al., Nat. Commun. 2025",
    capabilities=["single_step"],
    url="https://github.com/jogjogee/RSGPT",
)

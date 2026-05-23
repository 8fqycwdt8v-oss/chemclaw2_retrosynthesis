"""NeuralSym — reimplementation of Segler & Waller's template relevance
network (linminhtoo)."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="neuralsym",
    family="template",
    license="MIT",
    citation="Segler & Waller, Chem. Eur. J. 2017 (reimpl. by Lin)",
    capabilities=["single_step"],
    url="https://github.com/linminhtoo/neuralsym",
)

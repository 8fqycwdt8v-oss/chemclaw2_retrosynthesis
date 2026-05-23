"""Syntheseus — Microsoft's unified retrosynthesis benchmarking package.

Syntheseus internally wraps Chemformer / LocalRetro / RetroKnn / GLN /
RootAligned / MEGAN / etc. via uniform runners. Hosting it as a backend
gives us several models "for free" inside one container, at the cost of
not being able to ensemble across Syntheseus's *internal* models in our
aggregator (they would all appear as a single ``syntheseus`` backend).
"""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="syntheseus",
    family="planner",
    license="MIT",
    citation="Maziarz et al., Faraday Discuss. 2024",
    capabilities=["single_step", "multi_step"],
    url="https://github.com/microsoft/syntheseus",
)

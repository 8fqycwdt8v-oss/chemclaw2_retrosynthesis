"""AiZynthFinder adapter.

Phase 1 keeps AiZynthFinder in its own microservice (Docker image, own
conda env with TF + ONNX). The container exposes the same uniform
``/predict`` and ``/plan`` HTTP contract as every other backend, so the
gateway just talks to it via :class:`RemoteBackend`.

This adapter exists so the gateway has a canonical name (``aizynth``)
and an explicit BackendInfo independent of the container's `/info`.
"""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="aizynth",
    family="planner",
    license="MIT",
    citation="Genheden & Bjerrum, J. Cheminf. 2020; AiZynthFinder 4.0, 2024",
    capabilities=["single_step", "multi_step"],
    url="https://github.com/MolecularAI/aizynthfinder",
)

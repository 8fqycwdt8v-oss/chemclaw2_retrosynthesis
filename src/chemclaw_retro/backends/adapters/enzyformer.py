"""Enzyformer — two-stage pretrained model for enzymatic retrosynthesis."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="enzyformer",
    family="biocatalysis",
    license="MIT",
    citation="ChemRxiv 2025 (chemrxiv-2025-8ggs5)",
    capabilities=["single_step"],
    url="https://chemrxiv.org/doi/full/10.26434/chemrxiv-2025-8ggs5",
)

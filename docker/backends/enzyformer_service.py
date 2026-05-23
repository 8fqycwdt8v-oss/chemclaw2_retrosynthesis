"""Enzyformer service — placeholder until the upstream repo is public.
Reports unavailable via the standard /healthz contract."""

from __future__ import annotations

from typing import Any

from _base import Backend, make_app


class EnzyformerBackend(Backend):
    name = "enzyformer"
    family = "biocatalysis"
    license = "MIT"
    citation = "ChemRxiv 2025 (chemrxiv-2025-8ggs5)"
    url = "https://chemrxiv.org/doi/full/10.26434/chemrxiv-2025-8ggs5"
    capabilities = ["single_step"]

    def load(self) -> None:
        raise RuntimeError(
            "Enzyformer upstream code not yet public; remove `enabled: false` "
            "from the compose entry once the authors release the repo."
        )

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        return []


app = make_app(EnzyformerBackend())

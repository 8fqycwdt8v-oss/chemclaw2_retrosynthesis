"""Chemformer microservice — wraps MolecularAI's Chemformer for both
retrosynthesis (single-step) and forward synthesis."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, make_app


class ChemformerBackend(Backend):
    name = "chemformer"
    family = "transformer"
    license = "Apache-2.0"
    citation = "Irwin et al., Mach. Learn.: Sci. Technol. 2022"
    url = "https://github.com/MolecularAI/Chemformer"
    capabilities = ["single_step", "forward"]

    def __init__(self) -> None:
        self.model = None
        self.tokeniser = None

    def load(self) -> None:
        if self.model is not None:
            return
        from molbart.models.transformer_models import BARTModel  # type: ignore[import-not-found]
        from molbart.utils.tokenizers import ChemformerTokenizer  # type: ignore[import-not-found]

        ckpt = os.environ.get("CHEMFORMER_CKPT", "/weights/chemformer/combined.ckpt")
        tok_path = os.environ.get("CHEMFORMER_VOCAB", "/weights/chemformer/bart_vocab_downstream.json")
        self.tokeniser = ChemformerTokenizer(filename=tok_path)
        self.model = BARTModel.load_from_checkpoint(ckpt)
        self.model.eval()

    def _generate(self, src: str, top_k: int, *, reverse: bool) -> list[tuple[str, float]]:
        import torch  # type: ignore[import-not-found]

        tokens = self.tokeniser([src], pad=True)
        with torch.no_grad():
            preds, log_probs = self.model.sample_molecules(
                tokens, sampling_alg="beam", num_beams=top_k
            )
        out = []
        for p, lp in zip(preds[0][:top_k], log_probs[0][:top_k]):
            out.append((p, float(lp.exp())))
        return out

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        return [
            {"reactants": r.split("."), "score": s, "rank": i}
            for i, (r, s) in enumerate(self._generate(smiles, top_k, reverse=True))
        ]

    def forward(self, reactants: list[str], top_k: int) -> list[dict[str, Any]]:
        src = ".".join(reactants)
        return [{"smiles": p, "score": s} for p, s in self._generate(src, top_k, reverse=False)]


app = make_app(ChemformerBackend())

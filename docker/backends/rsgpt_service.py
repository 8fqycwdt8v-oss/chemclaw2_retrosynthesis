"""RSGPT service."""

from __future__ import annotations

import os
from typing import Any

from _base import Backend, make_app


class RSGPTBackend(Backend):
    name = "rsgpt"
    family = "llm"
    license = "MIT"
    citation = "Liu et al., Nat. Commun. 2025"
    url = "https://github.com/jogjogee/RSGPT"
    capabilities = ["single_step"]

    def __init__(self) -> None:
        self.pipe = None

    def load(self) -> None:
        if self.pipe is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import-not-found]

        ckpt = os.environ.get("RSGPT_CKPT", "/weights/rsgpt")
        tok = AutoTokenizer.from_pretrained(ckpt)
        mod = AutoModelForCausalLM.from_pretrained(ckpt)
        self.pipe = (tok, mod.eval())

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        import torch  # type: ignore[import-not-found]
        tok, mod = self.pipe
        ids = tok(smiles, return_tensors="pt").input_ids
        with torch.no_grad():
            out = mod.generate(
                ids, max_new_tokens=192, num_beams=top_k, num_return_sequences=top_k
            )
        decoded = tok.batch_decode(out, skip_special_tokens=True)
        return [
            {"reactants": d.split(">>")[0].split(".") if ">>" in d else d.split("."),
             "score": 1.0 - i * 0.05, "rank": i}
            for i, d in enumerate(decoded[:top_k])
        ]


app = make_app(RSGPTBackend())

"""Shared HuggingFace-LLM backend. Reused by ChemDFM, BatGPT-Chem,
RetroDFM-R, and other chat-style chemistry models.

Pass the upstream model id and a prompt template via env so the same
image can host different LLMs by changing env vars."""

from __future__ import annotations

import os
import re
from typing import Any

from _base import Backend, make_app

DEFAULT_TEMPLATE = (
    "You are an expert organic chemist. Given a product SMILES, propose "
    "{top_k} disconnection reactant sets, one per line as a "
    "dot-separated SMILES list, ordered best-first. Do not add commentary.\n"
    "Product: {smiles}\nReactants:"
)


class HFLLMBackend(Backend):
    family = "llm"

    def __init__(self) -> None:
        self.tokenizer = None
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import-not-found]
        import torch  # type: ignore[import-not-found]

        model_id = os.environ.get("HF_MODEL_ID")
        if not model_id:
            raise RuntimeError("HF_MODEL_ID env var not set")
        revision = os.environ.get("HF_REVISION", "main")
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, torch_dtype=dtype, device_map="auto",
            trust_remote_code=True,
        )
        self.model.eval()

    def _ask(self, prompt: str, top_k: int) -> str:
        import torch  # type: ignore[import-not-found]

        tok = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **tok,
                max_new_tokens=64 * top_k,
                do_sample=False,
                num_beams=max(1, top_k),
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        text = self.tokenizer.decode(out[0][tok["input_ids"].shape[1]:], skip_special_tokens=True)
        return text

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        template = os.environ.get("LLM_PROMPT_TEMPLATE", DEFAULT_TEMPLATE)
        prompt = template.format(smiles=smiles, top_k=top_k)
        completion = self._ask(prompt, top_k)
        # Each line: dot-separated reactant SMILES. Strip numbering and
        # markdown bullets defensively.
        out: list[dict[str, Any]] = []
        for rank, line in enumerate(completion.splitlines()):
            line = re.sub(r"^[\s\d\.\-\*\)]+", "", line).strip()
            if not line:
                continue
            out.append({"reactants": line.split("."), "score": 1.0 - rank * 0.05, "rank": rank})
            if len(out) >= top_k:
                break
        return out

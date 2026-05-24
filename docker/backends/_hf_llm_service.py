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

    def _ask(self, prompt: str, top_k: int) -> list[str]:
        """Return ``top_k`` independent beams.

        Critical: ``num_return_sequences`` must equal ``num_beams`` to
        actually emit ``top_k`` distinct beams. Returning a single
        sequence regardless of beam width silently collapses every LLM
        backend to top-1.
        """
        import torch  # type: ignore[import-not-found]

        beams = max(1, top_k)
        tok = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **tok,
                max_new_tokens=128,
                do_sample=False,
                num_beams=beams,
                num_return_sequences=beams,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        prompt_len = tok["input_ids"].shape[1]
        return [
            self.tokenizer.decode(out[i][prompt_len:], skip_special_tokens=True)
            for i in range(out.shape[0])
        ]

    def predict(self, smiles: str, top_k: int) -> list[dict[str, Any]]:
        template = os.environ.get("LLM_PROMPT_TEMPLATE", DEFAULT_TEMPLATE)
        prompt = template.format(smiles=smiles, top_k=top_k)
        completions = self._ask(prompt, top_k)
        # Each beam yields one reactant set; take the first non-empty
        # cleaned line of each completion as that beam's reactants.
        out: list[dict[str, Any]] = []
        for rank, completion in enumerate(completions):
            for line in completion.splitlines():
                line = re.sub(r"^[\s\d\.\-\*\)]+", "", line).strip()
                if line:
                    out.append(
                        {
                            "reactants": line.split("."),
                            "score": 1.0 - rank * 0.05,
                            "rank": rank,
                        }
                    )
                    break
            if len(out) >= top_k:
                break
        return out

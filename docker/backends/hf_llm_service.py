"""Generic HuggingFace-LLM backend.

A single image hosts every LLM-style chemistry model — ChemDFM,
BatGPT-Chem, RetroDFM-R, RSGPT, etc. — driven by env config:

* ``HF_MODEL_ID``   — HuggingFace repo id, OR
* ``HF_MODEL_PATH`` — local checkpoint directory mounted into /weights
* ``BACKEND_NAME``     — what /info reports
* ``BACKEND_CITATION`` / ``BACKEND_URL`` / ``BACKEND_LICENSE``
* ``LLM_PROMPT_TEMPLATE`` — override the default disconnection prompt
* ``HF_REVISION`` — HuggingFace revision (default ``main``)

Set in docker compose per-service so adding a new chemistry LLM is a
compose-only change.
"""

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
        self.name = os.environ.get("BACKEND_NAME", "hf-llm")
        self.license = os.environ.get("BACKEND_LICENSE", "Apache-2.0")
        self.citation = os.environ.get("BACKEND_CITATION") or None
        self.url = os.environ.get("BACKEND_URL") or None
        self.capabilities = ["single_step"]
        self.tokenizer = None
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        import torch  # type: ignore[import-not-found]
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import-not-found]

        source = os.environ.get("HF_MODEL_PATH") or os.environ.get("HF_MODEL_ID")
        if not source:
            raise RuntimeError(
                "neither HF_MODEL_PATH nor HF_MODEL_ID is set; refusing to start "
                f"backend {self.name!r}"
            )
        revision = os.environ.get("HF_REVISION", "main")
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(
            source, revision=revision, trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            source,
            revision=revision,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model.eval()

    def _ask(self, prompt: str, top_k: int) -> list[str]:
        """Return ``top_k`` beams. ``num_return_sequences`` must equal
        ``num_beams`` — anything less collapses to top-1."""
        import torch  # type: ignore[import-not-found]

        beams = max(1, top_k)
        max_new = int(os.environ.get("LLM_MAX_NEW_TOKENS", "128"))
        tok = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **tok,
                max_new_tokens=max_new,
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
        out: list[dict[str, Any]] = []
        for rank, completion in enumerate(completions):
            for raw in completion.splitlines():
                line = re.sub(r"^[\s\d\.\-\*\)]+", "", raw).strip()
                if line:
                    # Strip a reactants>>products fragment if the model
                    # decoded the full reaction SMILES.
                    if ">>" in line:
                        line = line.split(">>", 1)[0]
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


app = make_app(HFLLMBackend())

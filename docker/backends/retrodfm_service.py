"""RetroDFM-R service — chain-of-thought reasoning LLM."""

from _base import make_app
from _hf_llm_service import HFLLMBackend

PROMPT = (
    "You are a retrosynthesis expert. Reason step by step about the "
    "target product SMILES, then output the top {top_k} candidate "
    "reactant sets as dot-separated SMILES, one per line, no commentary.\n"
    "Product: {smiles}\nReactants:"
)


class RetroDFM(HFLLMBackend):
    name = "retrodfm"
    license = "Apache-2.0"
    citation = "arXiv:2507.17448"
    url = "https://arxiv.org/abs/2507.17448"
    capabilities = ["single_step"]


import os
os.environ.setdefault("LLM_PROMPT_TEMPLATE", PROMPT)
app = make_app(RetroDFM())

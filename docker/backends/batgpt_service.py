"""BatGPT-Chem service."""

from _base import make_app
from _hf_llm_service import HFLLMBackend


class BatGPT(HFLLMBackend):
    name = "batgpt"
    license = "Apache-2.0"
    citation = "Liu et al., arXiv:2408.10285"
    url = "https://arxiv.org/abs/2408.10285"
    capabilities = ["single_step"]


app = make_app(BatGPT())

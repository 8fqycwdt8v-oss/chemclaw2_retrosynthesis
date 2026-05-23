"""ChemDFM-13B service."""

from _base import make_app
from _hf_llm_service import HFLLMBackend


class ChemDFM(HFLLMBackend):
    name = "chemdfm"
    license = "Apache-2.0"
    citation = "Zhao et al., arXiv:2401.14818"
    url = "https://huggingface.co/OpenDFM/ChemDFM-13B-v1.0"
    capabilities = ["single_step"]


app = make_app(ChemDFM())

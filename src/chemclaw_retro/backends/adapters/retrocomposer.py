"""RetroComposer — composes templates for template-based retrosynthesis."""

from __future__ import annotations

from ...schemas import BackendInfo

INFO = BackendInfo(
    name="retrocomposer",
    family="template",
    license="MIT",
    citation="Yan et al., Biomolecules 2022",
    capabilities=["single_step"],
    url="https://github.com/uta-smile/RetroComposer",
)

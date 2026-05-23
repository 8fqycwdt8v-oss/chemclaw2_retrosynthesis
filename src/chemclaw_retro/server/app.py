"""FastAPI app factory + ASGI entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from .. import __version__
from .mcp import mount_mcp
from .routes import classify, conditions, forward, meta, multi_step, score, single_step

log = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="chemclaw-retro",
        version=__version__,
        summary=(
            "Meta-model retrosynthesis MCP server. Ensembles every "
            "open-source retrosynthesis engine into a single API surface "
            "with provenance + round-trip validation."
        ),
    )
    app.include_router(single_step.router)
    app.include_router(multi_step.router)
    app.include_router(forward.router)
    app.include_router(score.router)
    app.include_router(classify.router)
    app.include_router(conditions.router)
    app.include_router(meta.router)

    mount_mcp(app)
    return app


app = create_app()

"""Mount the FastAPI routes as an MCP server via ``fastapi-mcp``.

We keep this in its own module so swapping for ``FastMCP`` later is a
single-file change.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

log = logging.getLogger(__name__)


def mount_mcp(app: FastAPI) -> None:
    try:
        from fastapi_mcp import FastApiMCP  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover
        log.warning("fastapi-mcp not installed; MCP surface disabled")
        return

    mcp = FastApiMCP(
        app,
        name="chemclaw-retro",
        description=(
            "Open-source retrosynthesis meta-model. Exposes single-step "
            "(ensemble), multi-step planning, forward synthesis, "
            "synthesizability scoring, reaction classification, and "
            "condition recommendation as MCP tools."
        ),
    )
    # Mounts under /mcp by default; consumer agents (chemclaw2) connect via
    # Streamable HTTP at http://<host>:<port>/mcp.
    mount = getattr(mcp, "mount_http", None) or mcp.mount
    mount()

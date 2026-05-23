"""Typer CLI for local development + smoke-testing the gateway."""

from __future__ import annotations

import asyncio
import json

import typer
import uvicorn

from .config import get_settings

app = typer.Typer(help="chemclaw-retro CLI.")
serve_app = typer.Typer(help="Serving commands.")
app.add_typer(serve_app, name="mcp")


@serve_app.command("serve")
def serve(
    host: str = typer.Option(None, help="Bind host (defaults to settings)."),
    port: int = typer.Option(None, help="Bind port (defaults to settings)."),
    reload: bool = typer.Option(False, help="Reload on code changes (dev only)."),
) -> None:
    """Run the FastAPI + MCP gateway."""
    settings = get_settings()
    uvicorn.run(
        "chemclaw_retro.server.app:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
        log_level=settings.log_level,
    )


@app.command("backends")
def backends() -> None:
    """Print the currently enabled backends as JSON."""
    from .backends.registry import all_backends

    async def _run() -> None:
        infos = []
        for name, b in all_backends().items():
            try:
                info = await b.info()
                info.healthy = await b.healthz()
                infos.append(info.model_dump())
            except Exception as e:
                infos.append({"name": name, "error": str(e)})
        typer.echo(json.dumps(infos, indent=2))

    asyncio.run(_run())


@app.command("smoke")
def smoke(smiles: str = typer.Argument("CC(=O)Oc1ccccc1C(=O)O", help="Target SMILES")) -> None:
    """Run a single-step call against the in-process logic without HTTP."""
    from .canonical import canonical_smiles

    typer.echo(f"canonical: {canonical_smiles(smiles)}")


if __name__ == "__main__":  # pragma: no cover
    app()

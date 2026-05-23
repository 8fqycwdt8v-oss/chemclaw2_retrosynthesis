"""Runtime configuration — read from environment via pydantic-settings.

Backend URLs default to the docker-compose service names so a stock
``docker compose up`` works without any env tweaking.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendEndpoint(BaseSettings):
    """One backend microservice's URL + timeout."""

    url: str
    timeout_s: float = 30.0
    enabled: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHEMCLAW_RETRO_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    auth_token: str | None = Field(
        default=None,
        description="If set, all MCP / HTTP requests must present this bearer token.",
    )

    # Path to YAML weights for the heuristic aggregator.
    weights_path: Path = Path(__file__).parent / "meta" / "weights.yaml"

    # Reranker selection: "heuristic" (default) or "learned" (LightGBM).
    reranker: str = "heuristic"
    learned_model: Path | None = None

    # Per-backend endpoints. Keep one default per backend; override via env:
    #   CHEMCLAW_RETRO_BACKEND_AIZYNTH__URL=http://aizynth:9000
    backend_aizynth: BackendEndpoint = BackendEndpoint(url="http://aizynth:9000", timeout_s=120.0)
    backend_retrosim: BackendEndpoint = BackendEndpoint(url="http://retrosim:9000", timeout_s=15.0)
    backend_chemformer: BackendEndpoint = BackendEndpoint(
        url="http://chemformer:9000", timeout_s=60.0
    )
    backend_localretro: BackendEndpoint = BackendEndpoint(
        url="http://localretro:9000", timeout_s=30.0, enabled=False
    )
    backend_mhnreact: BackendEndpoint = BackendEndpoint(
        url="http://mhnreact:9000", timeout_s=30.0, enabled=False
    )
    backend_graph2smiles: BackendEndpoint = BackendEndpoint(
        url="http://graph2smiles:9000", timeout_s=60.0, enabled=False
    )
    backend_megan: BackendEndpoint = BackendEndpoint(
        url="http://megan:9000", timeout_s=60.0, enabled=False
    )
    backend_rsmiles: BackendEndpoint = BackendEndpoint(
        url="http://rsmiles:9000", timeout_s=60.0, enabled=False
    )
    backend_graphretro: BackendEndpoint = BackendEndpoint(
        url="http://graphretro:9000", timeout_s=60.0, enabled=False
    )
    backend_retroformer: BackendEndpoint = BackendEndpoint(
        url="http://retroformer:9000", timeout_s=60.0, enabled=False
    )
    backend_neuralsym: BackendEndpoint = BackendEndpoint(
        url="http://neuralsym:9000", timeout_s=30.0, enabled=False
    )
    backend_gln: BackendEndpoint = BackendEndpoint(
        url="http://gln:9000", timeout_s=60.0, enabled=False
    )
    backend_t5chem: BackendEndpoint = BackendEndpoint(
        url="http://t5chem:9000", timeout_s=60.0, enabled=False
    )
    backend_askcos: BackendEndpoint = BackendEndpoint(
        url="http://askcos:9000", timeout_s=180.0, enabled=False
    )
    backend_syntheseus: BackendEndpoint = BackendEndpoint(
        url="http://syntheseus:9000", timeout_s=120.0, enabled=False
    )
    backend_directmultistep: BackendEndpoint = BackendEndpoint(
        url="http://dms:9000", timeout_s=120.0, enabled=False
    )
    backend_retrochimera: BackendEndpoint = BackendEndpoint(
        url="http://retrochimera:9000", timeout_s=120.0, enabled=False
    )
    backend_readretro: BackendEndpoint = BackendEndpoint(
        url="http://readretro:9000", timeout_s=120.0, enabled=False
    )
    backend_retrobiocat: BackendEndpoint = BackendEndpoint(
        url="http://retrobiocat:9000", timeout_s=60.0, enabled=False
    )
    backend_retrosynformer: BackendEndpoint = BackendEndpoint(
        url="http://retrosynformer:9000", timeout_s=120.0, enabled=False
    )

    # Phase 2-4 additions: every backend in the catalogue now has an
    # endpoint, disabled by default. Flip via env to bring online.
    backend_openretro: BackendEndpoint = BackendEndpoint(
        url="http://openretro:9000", timeout_s=60.0, enabled=False
    )
    backend_retrostar: BackendEndpoint = BackendEndpoint(
        url="http://retrostar:9000", timeout_s=120.0, enabled=False
    )
    backend_desp: BackendEndpoint = BackendEndpoint(
        url="http://desp:9000", timeout_s=120.0, enabled=False
    )
    backend_deepretro: BackendEndpoint = BackendEndpoint(
        url="http://deepretro:9000", timeout_s=300.0, enabled=False
    )
    backend_retropath: BackendEndpoint = BackendEndpoint(
        url="http://retropath:9000", timeout_s=120.0, enabled=False
    )
    backend_enzyformer: BackendEndpoint = BackendEndpoint(
        url="http://enzyformer:9000", timeout_s=60.0, enabled=False
    )
    backend_het_retro: BackendEndpoint = BackendEndpoint(
        url="http://het-retro:9000", timeout_s=60.0, enabled=False
    )
    backend_chemdfm: BackendEndpoint = BackendEndpoint(
        url="http://chemdfm:9000", timeout_s=180.0, enabled=False
    )
    backend_batgpt: BackendEndpoint = BackendEndpoint(
        url="http://batgpt:9000", timeout_s=180.0, enabled=False
    )
    backend_retrodfm: BackendEndpoint = BackendEndpoint(
        url="http://retrodfm:9000", timeout_s=180.0, enabled=False
    )
    backend_ttl: BackendEndpoint = BackendEndpoint(
        url="http://ttl:9000", timeout_s=120.0, enabled=False
    )
    backend_g2retro: BackendEndpoint = BackendEndpoint(
        url="http://g2retro:9000", timeout_s=60.0, enabled=False
    )
    backend_fusionretro: BackendEndpoint = BackendEndpoint(
        url="http://fusionretro:9000", timeout_s=60.0, enabled=False
    )
    backend_tied_twoway: BackendEndpoint = BackendEndpoint(
        url="http://tied-twoway:9000", timeout_s=60.0, enabled=False
    )
    backend_retrocomposer: BackendEndpoint = BackendEndpoint(
        url="http://retrocomposer:9000", timeout_s=60.0, enabled=False
    )
    backend_retroxpert: BackendEndpoint = BackendEndpoint(
        url="http://retroxpert:9000", timeout_s=60.0, enabled=False
    )
    backend_disconnection_chemformer: BackendEndpoint = BackendEndpoint(
        url="http://disc-chemformer:9000", timeout_s=60.0, enabled=False
    )
    backend_retroprime: BackendEndpoint = BackendEndpoint(
        url="http://retroprime:9000", timeout_s=60.0, enabled=False
    )
    backend_retrobridge: BackendEndpoint = BackendEndpoint(
        url="http://retrobridge:9000", timeout_s=60.0, enabled=False
    )
    backend_rsgpt: BackendEndpoint = BackendEndpoint(
        url="http://rsgpt:9000", timeout_s=120.0, enabled=False
    )
    backend_synplanner: BackendEndpoint = BackendEndpoint(
        url="http://synplanner:9000", timeout_s=120.0, enabled=False
    )

    # Scoring / classification / forward — typically co-located with the
    # gateway since they're lightweight, but can be moved out.
    forward_url: str = Field(
        default="http://chemformer:9000",
        description="Backend used for round-trip forward validation.",
    )

    max_concurrency: int = 16
    overall_timeout_s: float = 180.0


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

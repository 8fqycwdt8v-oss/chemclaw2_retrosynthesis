"""Catalogue is the single source of truth for docker/compose.yaml.

If this test fails: edit the matching adapter's ``deploy`` field in
``src/chemclaw_retro/backends/adapters/`` and re-run
``python scripts/gen_compose.py``, then commit the regenerated yaml.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def test_compose_yaml_matches_catalogue() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gen_compose.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, (
        "docker/compose.yaml is stale relative to the adapter catalogue.\n"
        "Re-run `python scripts/gen_compose.py` and commit.\n"
        f"stderr:\n{result.stderr}"
    )


def test_every_phase2plus_adapter_has_deploy() -> None:
    """Phase 2-4 backends must declare ``deploy``; Phase-1 ones (aizynth,
    retrosim) are owned by compose.cpu.yaml and intentionally omit it."""
    from chemclaw_retro.backends.adapters._catalogue import CATALOGUE

    phase1_owned_by_cpu_compose = {"aizynth", "retrosim"}
    missing_deploy = sorted(
        name
        for name, info in CATALOGUE.items()
        if info.deploy is None and name not in phase1_owned_by_cpu_compose
    )
    assert not missing_deploy, (
        "the following adapters have no `deploy=` and are not in the "
        f"compose.cpu.yaml allowlist: {missing_deploy}"
    )

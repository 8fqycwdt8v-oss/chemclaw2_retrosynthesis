"""Regression: per-request Budget clamps phase timeouts to remaining
wall-clock so slow earlier phases tighten the later ones, and the
total never blows ``request_timeout_s``."""

from __future__ import annotations

import time

from chemclaw_retro._budget import Budget


def test_phase_caps_clamp_to_remaining() -> None:
    b = Budget.fresh(
        total_s=10.0, per_backend_s=30.0, aggregate_s=30.0, round_trip_s=30.0
    )
    # All three phases see at most total_s no matter their raw cap.
    assert b.for_per_backend() <= 10.0
    assert b.for_aggregate() <= 10.0
    assert b.for_round_trip() <= 10.0


def test_remaining_decreases_with_wall_clock(monkeypatch) -> None:
    fake_now = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: fake_now[0])
    b = Budget.fresh(
        total_s=10.0, per_backend_s=10.0, aggregate_s=10.0, round_trip_s=10.0
    )
    assert b.remaining == 10.0
    fake_now[0] = 105.0
    assert abs(b.remaining - 5.0) < 1e-6
    fake_now[0] = 120.0
    assert b.remaining == 0.0  # clamped to non-negative


def test_phase_cap_below_remaining_wins() -> None:
    b = Budget.fresh(
        total_s=1000.0, per_backend_s=5.0, aggregate_s=10.0, round_trip_s=2.0
    )
    assert b.for_per_backend() == 5.0
    assert b.for_aggregate() == 10.0
    assert b.for_round_trip() == 2.0

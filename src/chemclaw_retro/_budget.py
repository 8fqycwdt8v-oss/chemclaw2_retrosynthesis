"""Per-request time budget.

The single_step route runs in three phases — backend fan-out, feature
aggregation, and forward round-trip — that previously each owned an
independent timeout knob. A :class:`Budget` consolidates them so each
phase draws from the same shared deadline and a slow earlier phase
shortens the budget the later phases get.

Phase-specific caps remain configurable, but they're bounded above by
the remaining wall-clock budget — never below it.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    """Snapshot of the time budget for one in-flight request."""

    started_at: float
    total_s: float
    per_backend_s: float
    aggregate_s: float
    round_trip_s: float

    @classmethod
    def fresh(
        cls,
        *,
        total_s: float,
        per_backend_s: float,
        aggregate_s: float,
        round_trip_s: float,
    ) -> Budget:
        return cls(
            started_at=time.monotonic(),
            total_s=total_s,
            per_backend_s=per_backend_s,
            aggregate_s=aggregate_s,
            round_trip_s=round_trip_s,
        )

    @property
    def remaining(self) -> float:
        return max(0.0, self.total_s - (time.monotonic() - self.started_at))

    def for_per_backend(self) -> float:
        """Per-backend timeout, capped by what's left of the request."""
        return min(self.per_backend_s, self.remaining)

    def for_aggregate(self) -> float:
        return min(self.aggregate_s, self.remaining)

    def for_round_trip(self) -> float:
        return min(self.round_trip_s, self.remaining)

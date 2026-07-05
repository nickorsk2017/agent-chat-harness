"""Run history for the orchestrator (in-memory; swap for a real store)."""

from __future__ import annotations

from master_orchestrator.schemas.plan import OrchestrationResult


class RunHistory:
    def __init__(self) -> None:
        self._runs: list[OrchestrationResult] = []

    def record(self, result: OrchestrationResult) -> None:
        self._runs.append(result)

    def recent(self, n: int = 20) -> list[OrchestrationResult]:
        return self._runs[-n:]


history = RunHistory()

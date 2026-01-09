from __future__ import annotations
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.application.events.task_events import TaskCompleted, TaskFailed, TaskQueued, TaskStarted

class TaskEventLogger:
    def __init__(self, logger: LoggerPort) -> None:
        self._logger = logger

    def on_task_queued(self, ev: TaskQueued) -> None:
        self._logger.debug(
            f"Task queued: {ev.command_name}",
            extra={"task_id": ev.task_id}
        )

    def on_task_started(self, ev: TaskStarted) -> None:
        self._logger.debug(
            f"Task started: {ev.command_name}",
            extra={"task_id": ev.task_id}
        )

    def on_task_completed(self, ev: TaskCompleted) -> None:
        msg = ev.result.get_message() if ev.result else "no result"
        self._logger.info(
            f"✅ [{ev.command_name}] {msg}",
            extra={"task_id": ev.task_id}
        )

    def on_task_failed(self, ev: TaskFailed) -> None:
        msg = ev.result.get_message() if ev.result else "no result"
        self._logger.error(
            f"❌ [{ev.command_name}] {msg}",
            extra={"task_id": ev.task_id}
        )

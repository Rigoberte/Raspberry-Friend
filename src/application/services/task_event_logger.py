from __future__ import annotations
from enum import IntEnum
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.application.events.task_events import TaskCompleted, TaskFailed, TaskQueued, TaskStarted, TaskEvent

class LoggerLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class TaskEventLogger:
    def __init__(self, logger: LoggerPort) -> None:
        self._logger = logger

    def on_task_queued(self, ev: TaskQueued) -> None:
        now = ev.occurred_at.strftime("%H:%M:%S")
        self._logger.debug(
            f"[{now}] Task queued: {ev.command_name}",
            extra={"task_id": ev.task_id}
        )

    def on_task_started(self, ev: TaskStarted) -> None:
        now = ev.occurred_at.strftime("%H:%M:%S")
        self._logger.debug(
            message=f"[{now}] Task started: {ev.command_name}",
            extra={"task_id": ev.task_id}
        )

    def on_task_completed(self, ev: TaskCompleted) -> None:
        msg = self.__common_format__(ev)
        self._logger.info(
            message=f"✅ {msg}",
            extra={"task_id": ev.task_id}
        )

    def on_task_failed(self, ev: TaskFailed) -> None:
        msg = self.__common_format__(ev)
        self._logger.error(
            message=f"❌ {msg}",
            extra={"task_id": ev.task_id}
        )

    def __common_format__(self, ev: TaskCompleted | TaskFailed) -> str:
        msg = ev.result.get_message() if ev.result else "no result"
        if msg.find("\n") != -1:
            msg = "\n" + msg + "\n"
        
        time = ev.occurred_at.strftime("%H:%M:%S")

        return f"[{time}] {msg}"
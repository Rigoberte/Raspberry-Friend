from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from src.domain.events.music_events import PlaybackStarted, PlaybackStopped, PlaybackProgress
from src.domain.models.command import Command
from src.domain.models.tasks.continuous_task import ContinuousTask
from src.domain.ports.outbound.event_bus_ports import EventBusPort

if TYPE_CHECKING:
    from src.application.services.task_scheduler import TaskScheduler


class ProgressMonitorService:
    """
    Escucha eventos de inicio/parada de reproducción y automáticamente
    crea/destruye tareas continuas para monitorear el progreso.
    """

    def __init__(self, scheduler: TaskScheduler, event_bus: EventBusPort) -> None:
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._progress_tasks: dict[str, str] = {}
        
        event_bus.subscribe(PlaybackStarted, self._on_playback_started)
        event_bus.subscribe(PlaybackStopped, self._on_playback_stopped)

    def _on_playback_started(self, ev: PlaybackStarted) -> None:
        if ev.path in self._progress_tasks:
            return

        task = ContinuousTask(
            command=Command("monitor-playback", {
                "path": ev.path,
                "track": ev.track,
                "duration_ms": ev.duration_ms,
            }),
            check_interval=timedelta(milliseconds=500),
            condition_checker=lambda: True,
            max_executions=None,
            priority=1,
        )
        
        task_id = task.get_id()
        self._scheduler.add_task(task)
        self._progress_tasks[ev.path] = task_id

    def _on_playback_stopped(self, ev: PlaybackStopped) -> None:
        if ev.path not in self._progress_tasks:
            return

        task_id = self._progress_tasks.pop(ev.path)
        tasks = self._scheduler.list_tasks()
        
        for task in tasks:
            if task.get_id() == task_id:
                self._scheduler.remove_task(task)
                break

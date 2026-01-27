from __future__ import annotations
from datetime import datetime

from src.domain.events.music_events import PlaybackProgress, PlaybackStarted, PlaybackStopped
from src.domain.ports.outbound.logger_ports import LoggerPort
from src.application.services.task_event_logger import LoggerLevel


class MusicEventLogger:
    """Simple logger for music playback events."""

    def __init__(self, logger: LoggerPort, level: LoggerLevel = LoggerLevel.INFO) -> None:
        self._logger = logger
        self._level = level

    def on_playback_started(self, ev: PlaybackStarted) -> None:
        dur_s = ev.duration_ms / 1000 if ev.duration_ms else 0
        now = ev.occurred_at.strftime("%H:%M:%S") if isinstance(ev.occurred_at, datetime) else ""
        msg = f"▶️ [{now}] {ev.track or ev.path} | 0.0s / {dur_s:.1f}s"
        self._logger.info(msg)
    
    def on_playback_stopped(self, ev: PlaybackStopped) -> None:
        now = ev.occurred_at.strftime("%H:%M:%S") if isinstance(ev.occurred_at, datetime) else ""
        msg = f"⏸️ [{now}] {ev.track or ev.path} | Stopped"
        self._logger.info(msg)

    def on_progress(self, ev: PlaybackProgress) -> None:
        if self._level > LoggerLevel.DEBUG:
            return
        pos_s = ev.position_ms / 1000 if ev.position_ms else 0
        dur_s = ev.duration_ms / 1000 if ev.duration_ms else 0
        msg = f"[music progress] {ev.track or ev.path} {pos_s:.1f}s / {dur_s:.1f}s"
        self._logger.debug(msg, replace=True)
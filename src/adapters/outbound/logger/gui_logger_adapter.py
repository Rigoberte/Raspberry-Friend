from __future__ import annotations
from typing import Any, Mapping, Optional

from src.domain.ports.outbound.logger_ports import LoggerPort
from src.adapters.inbound.gui.gui_window import GUIWindow
from src.application.services.task_event_logger import LoggerLevel

class GUILoggerAdapter(LoggerPort):
    def __init__(self, gui_window: GUIWindow, level: LoggerLevel) -> None:
        self.gui_window = gui_window
        self.level = level

    def debug(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.DEBUG):
            text = self.__fmt__("[🐞 DEBUG]", message, replace, extra)
            self.gui_window.add_output(text, LoggerLevel.DEBUG)

    def info(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.INFO):
            text = self.__fmt__("[ⓘ INFO]", message, replace, extra)
            self.gui_window.add_output(text, LoggerLevel.INFO)

    def warning(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.WARNING):
            text = self.__fmt__("[⚠️ WARNING]", message, replace, extra)
            self.gui_window.add_output(text, LoggerLevel.WARNING)

    def error(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.ERROR):
            text = self.__fmt__("[❌ ERROR]", message, replace, extra)
            self.gui_window.add_output(text, LoggerLevel.ERROR)

    def __should_print__(self, level: LoggerLevel) -> bool:
        return level >= self.level
    
    def __fmt__(self, level: str, message: str, replace: bool, extra: Optional[Mapping[str, Any]]) -> str:
        extra_part = ""
        if extra:
            extras = " ".join(f"{k}={v}" for k, v in extra.items())
            extra_part = f"({extras})"

        prefix = "\r" if replace else ""
        suffix = "\n" if "\n" in message else ""

        space = " " if extra_part else ""
        return f"{prefix}{level} {message}{space}{extra_part}{suffix}"
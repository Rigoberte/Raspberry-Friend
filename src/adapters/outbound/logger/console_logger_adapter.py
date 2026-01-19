from __future__ import annotations
from typing import Any, Mapping, Optional

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import ANSI

from src.domain.ports.outbound.logger_ports import LoggerPort
from src.application.services.task_event_logger import LoggerLevel

class ConsoleLoggerAdapter(LoggerPort):
    def __init__(self, level: LoggerLevel = LoggerLevel.INFO) -> None:
        self._level = level

    def __should_print__(self, level: LoggerLevel) -> bool:
        return level >= self._level

    def __fmt__(self, level: str, message: str, replace: bool, extra: Optional[Mapping[str, Any]]) -> str:
        extra_part = ""
        if extra:
            extras = " ".join(f"{k}={v}" for k, v in extra.items())    
            extra_part = f"({extras})"
            
        prefix = "\r" if replace else ""
        
        subfix = "\n" if "\n" in message else ""

        return f"{prefix}{level} {message} {extra_part}{subfix}"
    
    def debug(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.DEBUG):
            print_formatted_text(ANSI(self.__fmt__("[🐞 DEBUG]", message, replace, extra)))

    def info(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.INFO):
            print_formatted_text(ANSI(self.__fmt__("[ℹ️ INFO]", message, replace, extra)))

    def warning(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.WARNING):
            print_formatted_text(ANSI(self.__fmt__("[⚠️ WARN]", message, replace, extra)))
            
    def error(self, message: str, *, extra=None, replace=False) -> None:
        if self.__should_print__(LoggerLevel.ERROR):
            print_formatted_text(ANSI(self.__fmt__("[❌ ERROR]", message, replace, extra)))
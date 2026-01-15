import sys
import os
from pathlib import Path
import colorama
from prompt_toolkit import PromptSession

from src.adapters.container import build_assistant
from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.application.services.command_parser import CommandParser

from src.application.events.event_bus import InMemoryEventBus
from src.domain.events.task_events import TaskCompleted, TaskFailed, TaskQueued, TaskStarted
from src.domain.events.music_events import PlaybackProgress, PlaybackStarted, PlaybackStopped
from src.application.services.task_event_logger import TaskEventLogger
from src.application.services.music_event_logger import MusicEventLogger
from src.adapters.outbound.logger.console_logger_adapter import ConsoleLoggerAdapter
from src.application.services.task_event_logger import LoggerLevel

def main():
    events_bus = InMemoryEventBus()

    output_logger = ConsoleLoggerAdapter(level=LoggerLevel.INFO)
    event_logger = TaskEventLogger(output_logger)

    events_bus.subscribe(TaskQueued, event_logger.on_task_queued)
    events_bus.subscribe(TaskStarted, event_logger.on_task_started)
    events_bus.subscribe(TaskCompleted, event_logger.on_task_completed)
    events_bus.subscribe(TaskFailed, event_logger.on_task_failed)

    music_logger = MusicEventLogger(output_logger, level=LoggerLevel.INFO)
    events_bus.subscribe(PlaybackStarted, music_logger.on_playback_started)
    events_bus.subscribe(PlaybackStopped, music_logger.on_playback_stopped)
    events_bus.subscribe(PlaybackProgress, music_logger.on_progress)

    assistant, _, _ = build_assistant(event_bus=events_bus)
    
    # Crear caso de uso y parser
    execute_command_uc = ExecuteCommandUseCase(assistant, output_logger)
    parser = CommandParser()
    
    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    session = PromptSession()
    
    try:
        while True:
            user_input = str(session.prompt("> ")).strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                break

            try:
                # Parsear y ejecutar comando usando caso de uso
                command_name, args = parser.parse_with_args(user_input)
                execute_command_uc.execute(command_name, args)
                
            except ValueError as e:
                output_logger.error(f"Error de validación: {str(e)}")
            except Exception as e:
                output_logger.error(f"Error inesperado: {str(e)}")

    finally:
        assistant.stop()
        events_bus.stop()
        if sys.platform.startswith("win"):
            os._exit(0)

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.resolve()))
    colorama.just_fix_windows_console()
    main()
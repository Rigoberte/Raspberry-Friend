import sys
from pathlib import Path
import colorama
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from src.infrastructure.container import build_assistant
from src.domain.models.command import Command

from src.application.events.event_bus import InMemoryEventBus
from src.application.events.task_events import TaskCompleted, TaskFailed, TaskQueued, TaskStarted
from src.application.services.task_event_logger import TaskEventLogger
from src.adapters.outbound.logger.console_logger_adapter import ConsoleLoggerAdapter
from src.application.services.task_event_logger import LoggerLevel

def main():
    events_bus = InMemoryEventBus()

    output_logger = ConsoleLoggerAdapter(level=LoggerLevel.DEBUG)
    event_logger = TaskEventLogger(output_logger)

    events_bus.subscribe(TaskQueued, event_logger.on_task_queued)
    events_bus.subscribe(TaskStarted, event_logger.on_task_started)
    events_bus.subscribe(TaskCompleted, event_logger.on_task_completed)
    events_bus.subscribe(TaskFailed, event_logger.on_task_failed)

    assistant = build_assistant(event_bus=events_bus)
    print("Welcome to Raspberry-Friend CLI! Type 'exit' to quit.")

    session = PromptSession()
    
    try:
        with patch_stdout():
            while True:
                user_input = str(session.prompt("> ")).strip()
                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit"):
                    break

                parts = user_input.split(maxsplit=1)
                name = parts[0]
                args = {"text": parts[1]} if len(parts) > 1 else {}

                command = Command(name, args)

                assistant.handle_command(command)

    finally:
        assistant.stop()
        events_bus.stop()

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent.resolve()))
    colorama.just_fix_windows_console()
    main()
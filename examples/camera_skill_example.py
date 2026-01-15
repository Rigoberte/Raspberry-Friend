"""
Example script demonstrating the camera skill usage.

This script shows how to use the new "turn-on-camera" and "turn-off-camera" commands
with the CameraSkill.
"""

from src.adapters.container import build_assistant
from src.application.services.command_parser import CommandParser
from src.application.use_cases.execute_command_use_case import ExecuteCommandUseCase
from src.adapters.outbound.logger.console_logger_adapter import ConsoleLoggerAdapter
from src.application.services.task_event_logger import LoggerLevel
from src.application.events.event_bus import InMemoryEventBus


def example_camera_usage():
    """
    Example of how to use the camera skill.
    """
    # Build the assistant with all dependencies
    events_bus = InMemoryEventBus()
    assistant, _ = build_assistant(event_bus=events_bus)
    
    # Create logger and use case
    logger = ConsoleLoggerAdapter(level=LoggerLevel.INFO)
    execute_command_uc = ExecuteCommandUseCase(assistant, logger)
    parser = CommandParser()
    
    print("=" * 60)
    print("Camera Skill Example")
    print("=" * 60)
    
    # Example 1: Turn on camera
    print("\n1. Turning on the camera...")
    command_1 = parser.parse("turn-on-camera")
    result_1 = execute_command_uc.execute(command_1)
    print(f"   Result: {result_1.message}")
    
    # Example 2: Interact with camera (it will display until 'q' is pressed)
    print("\n2. Camera is now running. Press 'q' in the camera window to stop.")
    print("   (The camera window will remain open for you to see the feed)")
    
    # Example 3: Turn off camera (from code)
    print("\n3. Turning off the camera from code...")
    command_2 = parser.parse("turn-off-camera")
    result_2 = execute_command_uc.execute(command_2)
    print(f"   Result: {result_2.message}")
    
    print("\n" + "=" * 60)
    print("Camera skill demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    example_camera_usage()

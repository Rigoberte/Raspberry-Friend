"""
Unit tests for AssistantService.
"""

import pytest
from src.application.services.assistant_service import AssistantService
from src.application.services.task_scheduler import TaskScheduler
from src.application.services.skill_registry import SkillRegistry
from src.domain.models.command import Command, CommandResult


class MockSkill:
    """Mock skill for testing."""
    
    def get_name(self) -> str:
        return "mock"
    
    def can_handle(self, command: Command) -> bool:
        return command.get_name() == "mock"
    
    def supported_commands(self) -> list[str]:
        return ["mock"]
    
    def handle(self, command: Command) -> CommandResult:
        return CommandResult(success=True, message=f"Handled: {command.get_name()}")


class FailingSkill:
    """Mock skill that always fails."""
    
    def get_name(self) -> str:
        return "fail"
    
    def can_handle(self, command: Command) -> bool:
        return command.get_name() == "fail"
    
    def supported_commands(self) -> list[str]:
        return ["fail"]
    
    def handle(self, command: Command) -> CommandResult:
        return CommandResult(success=False, message="Skill failed")

class TestAssistantService:
    """Tests for AssistantService."""

    def test_handle_command_success(self):
        """Test that AssistantService successfully handles a registered command."""
        # Arrange
        registry = SkillRegistry()
        mock_skill = MockSkill()
        registry.register(mock_skill)
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)
        command = Command(name="mock", slots={"text": "Hello"})

        # Act
        result = service.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert "Handled: mock" in result.get_message()

    def test_handle_command_not_found(self):
        """Test that AssistantService returns error for non-existent command."""
        # Arrange
        registry = SkillRegistry()
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)
        command = Command(name="unknown", slots={})

        # Act
        result = service.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is False
        assert "unknown" in result.get_message().lower()
        assert "no encontrado" in result.get_message().lower()

    def test_handle_command_with_failing_skill(self):
        """Test that AssistantService returns the skill's failure result."""
        # Arrange
        registry = SkillRegistry()
        failing_skill = FailingSkill()
        registry.register(failing_skill)
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)
        command = Command(name="fail", slots={})

        # Act
        result = service.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is False
        assert "Skill failed" in result.get_message()

    def test_list_skills_empty(self):
        """Test that list_skills returns empty list when no skills registered."""
        # Arrange
        registry = SkillRegistry()
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)

        # Act
        skills = service.list_skills()

        # Assert
        assert skills == []

    def test_list_skills_with_registered_skills(self):
        """Test that list_skills returns all registered skill names."""
        # Arrange
        registry = SkillRegistry()
        
        class EchoSkill:
            def get_name(self) -> str:
                return "echo"
            def can_handle(self, command: Command) -> bool:
                return command.get_name() == "echo"
            def supported_commands(self) -> list[str]:
                return ["echo"]
            def handle(self, command: Command) -> CommandResult:
                return CommandResult(success=True, message="echo")
                
        class TimeSkill:
            def get_name(self) -> str:
                return "time"
            def can_handle(self, command: Command) -> bool:
                return command.get_name() == "time"
            def supported_commands(self) -> list[str]:
                return ["time"]
            def handle(self, command: Command) -> CommandResult:
                return CommandResult(success=True, message="time")
                
        class WeatherSkill:
            def get_name(self) -> str:
                return "weather"
            def can_handle(self, command: Command) -> bool:
                return command.get_name() == "weather"
            def supported_commands(self) -> list[str]:
                return ["weather"]
            def handle(self, command: Command) -> CommandResult:
                return CommandResult(success=True, message="weather")
        
        registry.register(EchoSkill())
        registry.register(TimeSkill())
        registry.register(WeatherSkill())
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)

        # Act
        skills = service.list_skills()

        # Assert
        assert len(skills) == 3
        assert "echo" in skills
        assert "time" in skills
        assert "weather" in skills

    def test_handle_command_with_multiple_skills(self):
        """Test that the correct skill is selected for a command."""
        # Arrange
        registry = SkillRegistry()
        
        class EchoSkill:
            def get_name(self) -> str:
                return "echo"
            def can_handle(self, command: Command) -> bool:
                return command.get_name() == "echo"
            def supported_commands(self) -> list[str]:
                return ["echo"]
            def handle(self, command: Command) -> CommandResult:
                return CommandResult(success=True, message="echo result")
                
        class TimeSkill:
            def get_name(self) -> str:
                return "time"
            def can_handle(self, command: Command) -> bool:
                return command.get_name() == "time"
            def supported_commands(self) -> list[str]:
                return ["time"]
            def handle(self, command: Command) -> CommandResult:
                return CommandResult(success=True, message="time result")
        
        registry.register(EchoSkill())
        registry.register(TimeSkill())
        scheduler = TaskScheduler(registry)
        service = AssistantService(registry, scheduler)
        command = Command(name="time", slots={})

        # Act
        result = service.handle_command(command)

        # Assert
        assert result.is_successful() is True
        assert "time result" in result.get_message()

"""
Unit tests for AssistantService.
"""

import pytest
from src.application.services.assistant_service import AssistantService
from src.application.services.skill_registry import SkillRegistry
from src.domain.models.command import Command, CommandResult


class MockSkill:
    """Mock skill for testing."""
    
    def handle(self, command: Command) -> CommandResult:
        return CommandResult(success=True, message=f"Handled: {command.get_name()}")


class FailingSkill:
    """Mock skill that always fails."""
    
    def handle(self, command: Command) -> CommandResult:
        return CommandResult(success=False, message="Skill failed")


class TestAssistantService:
    """Tests for AssistantService."""

    def test_handle_command_success(self):
        """Test that AssistantService successfully handles a registered command."""
        # Arrange
        registry = SkillRegistry()
        registry.register("echo", MockSkill())
        service = AssistantService(registry)
        command = Command(name="echo", slots={"text": "Hello"})

        # Act
        result = service.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert "Handled: echo" in result.get_message()

    def test_handle_command_not_found(self):
        """Test that AssistantService returns error for non-existent command."""
        # Arrange
        registry = SkillRegistry()
        service = AssistantService(registry)
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
        registry.register("fail", FailingSkill())
        service = AssistantService(registry)
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
        service = AssistantService(registry)

        # Act
        skills = service.list_skills()

        # Assert
        assert skills == []

    def test_list_skills_with_registered_skills(self):
        """Test that list_skills returns all registered skill names."""
        # Arrange
        registry = SkillRegistry()
        registry.register("echo", MockSkill())
        registry.register("time", MockSkill())
        registry.register("weather", MockSkill())
        service = AssistantService(registry)

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
        registry.register("echo", MockSkill())
        registry.register("time", MockSkill())
        service = AssistantService(registry)
        command = Command(name="time", slots={})

        # Act
        result = service.handle_command(command)

        # Assert
        assert result.is_successful() is True
        assert "time" in result.get_message()

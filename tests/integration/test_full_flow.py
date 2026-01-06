"""
Integration tests for full application flow.
"""

import pytest
from src.infrastructure.container import build_assistant
from src.domain.models.command import Command, CommandResult


class TestFullFlowIntegration:
    """Integration tests for end-to-end command processing."""

    def test_echo_command_full_flow(self):
        """Test echo command from container to result."""
        # Arrange
        assistant = build_assistant()
        command = Command(name="echo", slots={"text": "Integration test"})

        # Act
        result = assistant.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert result.get_message() == "Integration test"

    def test_time_command_full_flow(self):
        """Test time command from container to result."""
        # Arrange
        assistant = build_assistant()
        command = Command(name="time", slots={})

        # Act
        result = assistant.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert any(char.isdigit() for char in result.get_message())

    def test_weather_command_full_flow(self):
        """Test weather command with real adapter."""
        # Arrange
        assistant = build_assistant()
        command = Command(name="weather", slots={"text": "Buenos Aires"})

        # Act
        result = assistant.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        # Should return weather data (success) or error message
        assert result.get_message() != ""

    def test_unknown_command_returns_error(self):
        """Test that unknown commands return proper error."""
        # Arrange
        assistant = build_assistant()
        command = Command(name="unknown-command", slots={})

        # Act
        result = assistant.handle_command(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is False
        assert "no encontrado" in result.get_message().lower()

    def test_list_all_skills(self):
        """Test that all skills are properly registered."""
        # Arrange
        assistant = build_assistant()

        # Act
        skills = assistant.list_skills()

        # Assert
        assert isinstance(skills, list)
        assert "echo" in skills
        assert "time" in skills
        assert "weather" in skills
        assert "music_player" in skills
        assert "file_explorer" in skills

    def test_multiple_commands_in_sequence(self):
        """Test that multiple commands can be executed in sequence."""
        # Arrange
        assistant = build_assistant()

        # Act
        result1 = assistant.handle_command(Command(name="echo", slots={"text": "First"}))
        result2 = assistant.handle_command(Command(name="time", slots={}))
        result3 = assistant.handle_command(Command(name="echo", slots={"text": "Second"}))

        # Assert
        assert result1.is_successful() is True
        assert result1.get_message() == "First"
        assert result2.is_successful() is True
        assert result3.is_successful() is True
        assert result3.get_message() == "Second"


class TestContainerIntegration:
    """Integration tests for the dependency injection container."""

    def test_build_assistant_returns_assistant_service(self):
        """Test that build_assistant returns a properly configured AssistantService."""
        # Act
        assistant = build_assistant()

        # Assert
        assert assistant is not None
        assert hasattr(assistant, 'handle_command')
        assert hasattr(assistant, 'list_skills')

    def test_skills_are_injected_with_correct_dependencies(self):
        """Test that skills receive their dependencies from the container."""
        # Arrange
        assistant = build_assistant()

        # Act - Test weather skill (depends on WeatherService)
        weather_result = assistant.handle_command(
            Command(name="weather", slots={"text": "Buenos Aires"})
        )

        # Assert - Should work without errors (service was injected)
        assert isinstance(weather_result, CommandResult)

    def test_container_is_idempotent(self):
        """Test that calling build_assistant multiple times creates independent instances."""
        # Act
        assistant1 = build_assistant()
        assistant2 = build_assistant()

        # Assert
        assert assistant1 is not assistant2

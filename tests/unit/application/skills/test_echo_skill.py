"""
Unit tests for EchoSkill.
"""

import pytest
from src.application.use_cases.skills.echo_skill import EchoSkill
from src.domain.models.command import Command, CommandResult


class TestEchoSkill:
    """Tests for EchoSkill."""

    def test_can_handle_echo_command(self):
        """Test that EchoSkill can handle 'echo' commands."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="echo", slots={"text": "Hello"})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_can_handle_echo_case_insensitive(self):
        """Test that EchoSkill handles 'echo' case-insensitively."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="ECHO", slots={"text": "Hello"})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_cannot_handle_other_commands(self):
        """Test that EchoSkill cannot handle non-echo commands."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="weather", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is False

    def test_handle_echo_returns_text(self):
        """Test that EchoSkill returns the provided text."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="echo", slots={"text": "Hello World"})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert result.get_message() == "Hello World"

    def test_handle_echo_with_empty_text(self):
        """Test that EchoSkill handles empty text gracefully."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="echo", slots={})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert result.get_message() == ""

    def test_handle_echo_with_special_characters(self):
        """Test that EchoSkill handles special characters."""
        # Arrange
        skill = EchoSkill()
        command = Command(name="echo", slots={"text": "!@#$%^&*()"})

        # Act
        result = skill.handle(command)

        # Assert
        assert result.get_message() == "!@#$%^&*()"

"""
Unit tests for TimeSkill.
"""

import pytest
from datetime import datetime
from src.application.use_cases.skills.time_skill import TimeSkill
from src.domain.models.command import Command, CommandResult


class TestTimeSkill:
    """Tests for TimeSkill."""

    def test_can_handle_time_command(self):
        """Test that TimeSkill can handle 'time' commands."""
        # Arrange
        skill = TimeSkill()
        command = Command(name="time", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_cannot_handle_other_commands(self):
        """Test that TimeSkill cannot handle non-time commands."""
        # Arrange
        skill = TimeSkill()
        command = Command(name="echo", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is False

    def test_handle_time_returns_current_time(self):
        """Test that TimeSkill returns current time."""
        # Arrange
        skill = TimeSkill()
        command = Command(name="time", slots={})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert result.get_message() != ""

    def test_handle_time_contains_time_info(self):
        """Test that the returned message contains time information."""
        # Arrange
        skill = TimeSkill()
        command = Command(name="time", slots={})

        # Act
        result = skill.handle(command)
        message = result.get_message()

        # Assert
        # Should contain numbers (hours, minutes, seconds)
        assert any(char.isdigit() for char in message)

    def test_handle_time_format(self):
        """Test that time is returned in expected format."""
        # Arrange
        skill = TimeSkill()
        command = Command(name="time", slots={})

        # Act
        result = skill.handle(command)
        message = result.get_message()

        # Assert
        # Should contain time separators (could be : or -)
        assert ":" in message or "-" in message or "Current" in message

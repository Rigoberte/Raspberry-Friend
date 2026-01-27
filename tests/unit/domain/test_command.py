"""
Unit tests for Command and CommandResult value objects.
"""

import pytest
from src.domain.models.command import Command, CommandResult


class TestCommand:
    """Tests for Command value object."""

    def test_command_creation_with_name_and_args(self):
        """Test that a Command can be created with name and arguments."""
        # Arrange & Act
        command = Command(name="echo", slots={"text": "Hello World"})

        # Assert
        assert command.get_name() == "echo"
        assert command.get_args() == {"text": "Hello World"}

    def test_command_creation_with_empty_args(self):
        """Test that a Command can be created with empty arguments."""
        # Arrange & Act
        command = Command(name="time", slots={})

        # Assert
        assert command.get_name() == "time"
        assert command.get_args() == {}

    def test_command_get_name_returns_string(self):
        """Test that get_name() returns a string."""
        # Arrange
        command = Command(name="weather", slots={"text": "Buenos Aires"})

        # Act
        name = command.get_name()

        # Assert
        assert isinstance(name, str)
        assert name == "weather"

    def test_command_get_args_returns_dict_copy(self):
        """Test that get_args() returns a copy of arguments."""
        # Arrange
        original_args = {"text": "test"}
        command = Command(name="echo", slots=original_args)

        # Act
        returned_args = command.get_args()
        returned_args["new_key"] = "new_value"

        # Assert - original should not be modified
        assert "new_key" not in command.get_args()


class TestCommandResult:
    """Tests for CommandResult value object."""

    def test_command_result_success_true(self):
        """Test CommandResult with success=True."""
        # Arrange & Act
        result = CommandResult(success=True, message="Operation successful")

        # Assert
        assert result.is_successful() is True
        assert result.get_message() == "Operation successful"

    def test_command_result_success_false(self):
        """Test CommandResult with success=False."""
        # Arrange & Act
        result = CommandResult(success=False, message="Operation failed")

        # Assert
        assert result.is_successful() is False
        assert result.get_message() == "Operation failed"

    def test_command_result_message_is_string(self):
        """Test that get_message() returns a string."""
        # Arrange
        result = CommandResult(success=True, message="Test message")

        # Act
        message = result.get_message()

        # Assert
        assert isinstance(message, str)

    def test_command_result_with_empty_message(self):
        """Test CommandResult with empty message."""
        # Arrange & Act
        result = CommandResult(success=True, message="")

        # Assert
        assert result.get_message() == ""
        assert result.is_successful() is True

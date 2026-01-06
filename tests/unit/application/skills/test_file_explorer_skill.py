"""
Unit tests for FileExplorerSkill.
"""

import pytest
from src.application.use_cases.skills.file_explorer_skill import FileExplorerSkill
from src.domain.models.command import Command, CommandResult


class TestFileExplorerSkill:
    """Tests for FileExplorerSkill."""

    def test_can_handle_file_explorer_command(self):
        """Test that FileExplorerSkill can handle 'file-explorer' commands."""
        # Arrange
        skill = FileExplorerSkill()
        command = Command(name="file-explorer", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_cannot_handle_other_commands(self):
        """Test that FileExplorerSkill cannot handle other commands."""
        # Arrange
        skill = FileExplorerSkill()
        command = Command(name="echo", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is False

    def test_handle_file_explorer_returns_result(self):
        """Test that FileExplorerSkill returns a CommandResult."""
        # Arrange
        skill = FileExplorerSkill()
        command = Command(name="file-explorer", slots={})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.get_message() != ""

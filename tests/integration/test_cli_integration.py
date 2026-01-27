"""
Integration tests for CLI adapter.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.adapters.inbound.cli import main
from src.domain.models.command import Command


class TestCLIIntegration:
    """Integration tests for the CLI adapter."""

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_processes_echo_command(self, mock_print, mock_session):
        """Test that CLI processes echo command correctly."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.side_effect = ["echo hello", "exit"]
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Verify that the echo message was printed
        assert any("hello" in str(call) for call in mock_print.call_args_list)

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_handles_exit_command(self, mock_print, mock_session):
        """Test that CLI exits properly on 'exit' command."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.return_value = "exit"
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Should exit without errors

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_handles_quit_command(self, mock_print, mock_session):
        """Test that CLI exits properly on 'quit' command."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.return_value = "quit"
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Should exit without errors

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_handles_empty_input(self, mock_print, mock_session):
        """Test that CLI handles empty input gracefully."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.side_effect = ["", "exit"]
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Should continue to next prompt without errors

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_handles_unknown_command(self, mock_print, mock_session):
        """Test that CLI handles unknown commands."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.side_effect = ["unknown-command", "exit"]
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Should print error message
        assert any("no encontrado" in str(call).lower() for call in mock_print.call_args_list)

    @patch('src.adapters.inbound.cli.PromptSession')
    @patch('builtins.print')
    def test_cli_processes_multiple_commands(self, mock_print, mock_session):
        """Test that CLI can process multiple commands in sequence."""
        # Arrange
        mock_prompt = MagicMock()
        mock_prompt.prompt.side_effect = [
            "echo first",
            "time",
            "echo second",
            "exit"
        ]
        mock_session.return_value = mock_prompt

        # Act
        main()

        # Assert
        # Should process all commands
        assert any("first" in str(call) for call in mock_print.call_args_list)
        assert any("second" in str(call) for call in mock_print.call_args_list)

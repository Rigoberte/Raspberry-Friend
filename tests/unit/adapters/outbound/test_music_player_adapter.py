"""
Unit tests for Music Player Adapters.
"""

import pytest
from src.domain.ports.outbound.music_player_ports import MusicPlayerPort
from src.adapters.outbound.music_player.mock_music_player_adapter import MockMusicPlayerPort


class TestMockMusicPlayerAdapter:
    """Tests for MockMusicPlayerPort adapter."""

    def test_mock_music_player_implements_interface(self):
        """Test that MockMusicPlayerPort implements MusicPlayerPort interface."""
        # Arrange & Act
        service = MockMusicPlayerPort()

        # Assert
        assert isinstance(service, MusicPlayerPort)

    def test_mock_play_song_returns_success(self):
        """Test that play_song returns success."""
        # Arrange
        service = MockMusicPlayerPort()

        # Act
        result = service.play_song("test.mp3")

        # Assert
        assert isinstance(result, dict)
        assert "success" in result

    def test_mock_pause_song_returns_success(self):
        """Test that pause_song returns success."""
        # Arrange
        service = MockMusicPlayerPort()

        # Act
        result = service.pause_song()

        # Assert
        assert isinstance(result, dict)
        assert "success" in result

    def test_mock_resume_song_returns_success(self):
        """Test that resume_song returns success."""
        # Arrange
        service = MockMusicPlayerPort()

        # Act
        result = service.resume_song()

        # Assert
        assert isinstance(result, dict)
        assert "success" in result

    def test_mock_stop_song_returns_success(self):
        """Test that stop_song returns success."""
        # Arrange
        service = MockMusicPlayerPort()

        # Act
        result = service.stop_song()

        # Assert
        assert isinstance(result, dict)
        assert "success" in result

    def test_mock_add_to_playlist_returns_success(self):
        """Test that add_to_playlist returns success."""
        # Arrange
        service = MockMusicPlayerPort()

        # Act
        result = service.add_to_playlist("test.mp3")

        # Assert
        assert isinstance(result, dict)
        assert "success" in result


# Note: PygameMusicPlayerService tests would require pygame to be initialized
# and are better suited for integration tests
class TestPygameMusicPlayerAdapter:
    """Tests for PygameMusicPlayerService adapter (basic checks only)."""

    @pytest.mark.skip(reason="Requires pygame initialization and audio hardware")
    def test_pygame_music_player_implements_interface(self):
        """Test that PygameMusicPlayerService implements MusicPlayerPort interface."""
        # This would require pygame setup
        pass

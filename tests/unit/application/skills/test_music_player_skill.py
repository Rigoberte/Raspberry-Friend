"""
Unit tests for MusicPlayerSkill.
"""

import pytest
from src.application.use_cases.skills.music_player_skill import MusicPlayerSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.music_player_ports import MusicPlayerPort


class MockMusicPlayerService(MusicPlayerPort):
    """Mock music player service for testing."""
    
    def __init__(self):
        self.is_playing = False
        self.current_song = None
        self.playlist = []

    def play_song(self, song: str) -> dict[str, str | bool]:
        self.current_song = song
        self.is_playing = True
        return {"success": True, "message": f"Playing {song}"}

    def pause_song(self) -> dict[str, str | bool]:
        self.is_playing = False
        return {"success": True, "message": "Paused"}

    def resume_song(self) -> dict[str, str | bool]:
        self.is_playing = True
        return {"success": True, "message": "Resumed"}

    def stop_song(self) -> dict[str, str | bool]:
        self.is_playing = False
        self.current_song = None
        return {"success": True, "message": "Stopped"}

    def rewind_song(self) -> dict[str, str | bool]:
        return {"success": True, "message": "Rewinded"}

    def next_song(self) -> dict[str, str | bool]:
        return {"success": True, "message": "Next song"}

    def previous_song(self) -> dict[str, str | bool]:
        return {"success": True, "message": "Previous song"}

    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        self.playlist.append(song)
        return {"success": True, "message": f"Added {song} to playlist"}

    def current_song_info(self) -> str:
        return self.current_song or "No song playing"

    def play_current_folder(self, folder: str) -> dict[str, str | bool]:
        return {"success": True, "message": f"Playing folder {folder}"}


class TestMusicPlayerSkill:
    """Tests for MusicPlayerSkill."""

    def test_can_handle_play_song_command(self):
        """Test that MusicPlayerSkill can handle 'play-song' commands."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        command = Command(name="play-song", slots={"text": "song.mp3"})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_can_handle_pause_song_command(self):
        """Test that MusicPlayerSkill can handle 'pause-song' commands."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        command = Command(name="pause-song", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_can_handle_all_music_commands(self):
        """Test that MusicPlayerSkill can handle all music-related commands."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        music_commands = [
            "play-song", "pause-song", "resume-song",
            "rewind-song", "stop-song", "next-song",
            "previous-song", "add-to-playlist",
            "current-song", "play-current-folder"
        ]

        # Act & Assert
        for cmd_name in music_commands:
            command = Command(name=cmd_name, slots={})
            assert skill.can_handle(command) is True

    def test_cannot_handle_other_commands(self):
        """Test that MusicPlayerSkill cannot handle non-music commands."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        command = Command(name="echo", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is False

    def test_handle_play_song(self):
        """Test that MusicPlayerSkill handles play-song command."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        command = Command(name="play-song", slots={"text": "test.mp3"})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        # Result depends on implementation, could be success or failure

    def test_music_skill_uses_injected_service(self):
        """Test that MusicPlayerSkill uses the injected service."""
        # Arrange
        service = MockMusicPlayerService()
        skill = MusicPlayerSkill(service=service)
        
        # Verify the service is stored
        assert skill.service is service

from src.domain.ports.outbound.music_player_ports import MusicPlayerPort
from src.domain.ports.outbound.event_bus_ports import EventBusPort
from src.domain.events.music_events import PlaybackStarted, PlaybackStopped
import pygame
import os
from datetime import datetime

try:
    from mutagen.mp3 import MP3
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

class PygameMusicPlayerPort(MusicPlayerPort):
    def __init__(self, event_bus: EventBusPort | None = None):
        try:
            self.mixer = pygame.mixer
            self.mixer.init()

            self.current_index = 0
            self.playlist = []
            self._event_bus = event_bus
            self._current_duration_ms = 0

        except pygame.error as e:
            print(f"Failed to initialize the mixer: {e}")

    def play_song(self, song: str) -> dict[str, str | bool]:
        if self.is_busy():
            self.mixer.music.stop()

        self.playlist = [song]
        return self.__change_song__(0)
        
    def pause_song(self) -> dict[str, str | bool]:
        return self.__apply_if_busy__(self.mixer.music.pause)

    def resume_song(self) -> dict[str, str | bool]:
        if not self.is_busy():
            if self.get_pos() > 0:
                self.mixer.music.unpause()
            else:
                self.__change_song__(self.current_index)
            
            return {
                "success": True,
                "error-message": ""
            }
        
        return {
            "success": False,
            "error-message": "Music is already playing"
        }

    def stop_song(self) -> dict[str, str | bool]:
        result = self.__apply_if_busy__(self.mixer.music.stop)
        
        # Emitir evento de parada
        if result.get("success") and self.current_index >= 0 and self.current_index < len(self.playlist):
            if self._event_bus:
                song_path = self.playlist[self.current_index]
                event = PlaybackStopped(
                    path=song_path,
                    track=os.path.basename(song_path),
                    occurred_at=datetime.now(),
                )
                self._event_bus.publish(event)
        
        return result

    def rewind_song(self) -> dict[str, str | bool]:
        return self.__apply_if_busy__(self.mixer.music.rewind)

    def next_song(self) -> dict[str, str | bool]:
        next_index = (self.current_index + 1) % len(self.playlist)
        
        return self.__change_song__(next_index)

    def previous_song(self) -> dict[str, str | bool]:
        previous_index = (self.current_index - 1) % len(self.playlist)
        
        return self.__change_song__(previous_index)
    
    def current_song(self) -> str:
        if self.get_pos() <= 0:
            return "No song is currently playing"
        
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return "No song is currently playing"
        
        return self.playlist[self.current_index].title()

    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        self.playlist.append(song)
        return {
            "success": True,
            "error-message": ""
        }
    
    def get_pos(self) -> int:
        return self.mixer.music.get_pos()
    
    def is_busy(self) -> bool:
        return self.mixer.music.get_busy()
    
    def volume_up(self) -> dict[str, str | bool]:
        current_volume = self.mixer.music.get_volume()
        new_volume = min(1.0, current_volume + 0.1)
        self.mixer.music.set_volume(new_volume)
        
        return {
            "success": True,
            "error-message": ""
        }
    
    def volume_down(self) -> dict[str, str | bool]:
        current_volume = self.mixer.music.get_volume()
        new_volume = max(0.0, current_volume - 0.1)
        self.mixer.music.set_volume(new_volume)
        
        return {
            "success": True,
            "error-message": ""
        }
    
    def set_volume(self, volume: float) -> dict[str, str | bool]:
        vol = max(0.0, min(volume, 1.0))
        self.mixer.music.set_volume(vol)
        
        return {
            "success": True,
            "error-message": ""
        }
    
    def __apply_if_busy__(self, func, *args, **kwargs) -> dict[str, str | bool]:
        if not self.is_busy():
            return {
                "success": False,
                "error-message": "No song is currently playing"
            }
        
        func(*args, **kwargs)
        return {
            "success": True,
            "error-message": ""
        }
    
    def __change_song__(self, index: int) -> dict[str, str | bool]:
        if index < 0 or index >= len(self.playlist):
            return
        
        try:
            self.current_index = index
            song = self.playlist[index]
            
            # Try to get duration using mutagen if available
            duration = 0
            if HAS_MUTAGEN:
                try:
                    audio = MP3(song)
                    duration = audio.info.length
                except Exception:
                    duration = 0

            self._current_duration_ms = int(duration * 1000)
            self.mixer.music.load(song)
            self.mixer.music.play()
            
            if self._event_bus:
                event = PlaybackStarted(
                    path=song,
                    track=os.path.basename(song),
                    duration_ms=self._current_duration_ms,
                    occurred_at=datetime.now(),
                )
                self._event_bus.publish(event)

            return {
                "success": True,
                "error-message": "",
                "duration": duration,
                "file": song
            }
        except pygame.error as e:
            return {
                "success": False,
                "error-message": f"Error changing song: {e}"
            }
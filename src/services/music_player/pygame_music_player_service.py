from .music_player_service import MusicPlayerService
import pygame
import os

class PygameMusicPlayerService(MusicPlayerService):
    def __init__(self):
        try:
            self.mixer = pygame.mixer
            self.mixer.init()

            self.current_index = 0
            self.playlist = []

        except pygame.error as e:
            print(f"Failed to initialize the mixer: {e}")

    def play_song(self, song: str) -> dict[str, str | bool]:
        if not os.path.isfile(song):
            return {
                "success": False,
                "error-message": "File does not exist"
            }
        
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
        return self.__apply_if_busy__(self.mixer.music.stop)

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
        
        return self.playlist[self.current_index]

    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        if not os.path.isfile(song):
            return {
                "success": False,
                "error-message": "File does not exist"
            }
        
        self.playlist.append(song)
        return {
            "success": True,
            "error-message": ""
        }
    
    def get_pos(self) -> int:
        return self.mixer.music.get_pos()
    
    def is_busy(self) -> bool:
        return self.mixer.music.get_busy()
    
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
            self.mixer.music.load(song)
            self.mixer.music.play()

            return {
                "success": True,
                "error-message": ""
            }
        except pygame.error as e:
            return {
                "success": False,
                "error-message": f"Error changing song: {e}"
            }
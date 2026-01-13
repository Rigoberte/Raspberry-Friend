from src.domain.ports.outbound.music_player_ports import MusicPlayerPort
from src.domain.ports.outbound.event_bus_ports import EventBusPort

class MockMusicPlayerPort(MusicPlayerPort):
    def __init__(self, event_bus: EventBusPort | None = None):
        self.current_index = 0
        self.playlist = []
        self._event_bus = event_bus

    def play_song(self, song: str) -> dict[str, str | int]:
        if song == "non_existent.mp3":
            return {
                "success": False,
                "error-message": "File does not exist"
            }
        
        self.playlist = [song]
        return self.__change_song__(0)
    
    def pause_song(self) -> dict[str, str | bool]:
        return self.__apply_if_busy__(lambda: None)
    
    def resume_song(self) -> dict[str, str | bool]:
        if not self.is_busy():
            if self.get_pos() > 0:
                return self.__apply_if_busy__(lambda: None)
            else:
                return self.__change_song__(self.current_index)
        
        return {
            "success": False,
            "error-message": "Music is already playing"
        }
    
    def stop_song(self) -> dict[str, str | bool]:
        return self.__apply_if_busy__(lambda: None)
    
    def rewind_song(self) -> dict[str, str | bool]:
        return self.__apply_if_busy__(lambda: None)
    
    def next_song(self) -> dict[str, str | bool]:
        next_index = (self.current_index + 1) % len(self.playlist)
        
        return self.__change_song__(next_index)
    
    def previous_song(self) -> dict[str, str | bool]:
        previous_index = (self.current_index - 1) % len(self.playlist)
        
        return self.__change_song__(previous_index)
    
    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        self.playlist.append(song)
        return {
            "success": True,
            "error-message": f"'{song}' added to playlist"
        }
    
    def current_song(self) -> str:
        if self.get_pos() <= 0:
            return "No song is currently playing"
        
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return "No song is currently playing"
        
        return self.playlist[self.current_index]
    
    def get_pos(self) -> int:
        if not self.is_busy():
            return 0
        return 1000 
    
    def is_busy(self) -> bool:
        return self.get_pos() > 0
    
    def __apply_if_busy__(self, func) -> dict[str, str | bool]:
        if not self.is_busy():
            return {
                "success": False,
                "error-message": "No song is currently playing"
            }
        
        func()
        return {
            "success": True,
            "error-message": ""
        }
    
    def __change_song__(self, index: int) -> dict[str, str | bool]:
        if index < 0 or index >= len(self.playlist):
            return {
                "success": False,
                "error-message": "Song index out of range"
            }
        
        self.current_index = index
        return {
            "success": True,
            "error-message": f"Now playing: {self.playlist[self.current_index]}"
        }
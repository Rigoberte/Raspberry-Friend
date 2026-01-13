from abc import ABC, abstractmethod

class MusicPlayerPort(ABC):
    """
    Abstract interface for obtaining weather information.
    """
    @abstractmethod
    def play_song(self, song: str) -> dict[str, str | int]:
        raise NotImplementedError

    @abstractmethod
    def pause_song(self) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def resume_song(self) -> dict[str, str | bool]:
        raise NotImplementedError
    
    @abstractmethod
    def stop_song(self) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def rewind_song(self) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def next_song(self) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def previous_song(self) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        raise NotImplementedError

    @abstractmethod
    def current_song(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_pos(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def is_busy(self) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def set_volume(self, volume: int) -> dict[str, str | bool]:
        raise NotImplementedError
    
    @abstractmethod
    def volume_up(self) -> dict[str, str | bool]:
        raise NotImplementedError
    
    @abstractmethod
    def volume_down(self) -> dict[str, str | bool]:
        raise NotImplementedError
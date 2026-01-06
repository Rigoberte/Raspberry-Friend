from abc import ABC, abstractmethod

class MusicPlayerPort(ABC):
    """
    Abstract interface for obtaining weather information.
    """
    @abstractmethod
    def play_song(self, song: str) -> dict[str, str | int]:
        pass

    @abstractmethod
    def pause_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def resume_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def stop_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def rewind_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def next_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def previous_song(self) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def add_to_playlist(self, song: str) -> dict[str, str | bool]:
        pass

    @abstractmethod
    def current_song(self) -> str:
        pass

    @abstractmethod
    def get_pos(self) -> int:
        pass

    @abstractmethod
    def is_busy(self) -> bool:
        pass
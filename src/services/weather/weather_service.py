from abc import ABC, abstractmethod

class WeatherService(ABC):
    """
    Abstract interface for obtaining weather information.
    """
    @abstractmethod
    def get_weather(self, city: str) -> dict[str, float | int | bool | str]:
        pass
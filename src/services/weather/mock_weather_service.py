from .weather_service import WeatherService

class MockWeatherService(WeatherService):
    """
    Placeholder weather service for testing purposes.
    Returns fixed weather data regardless of city.
    """

    def get_weather(self, city: str) -> dict[str, float | int | bool | str]:
        """
        Returns fake weather info for the given city.
        """
        info = {
            "success": True,
            "message": "Weather fetched successfully.",
            "temperature": 20.0,
            "apparent_temperature": 19.5,
            "precipitation_probability": 10,
            "visibility": 10000,
            "uv_index": 3,
            "sunshine_duration": 3600,
            "humidity": 50,
            "dew_point": 10,
            "is_day": True
        }

        return info
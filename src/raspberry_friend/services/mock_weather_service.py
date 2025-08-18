from .weather_service import WeatherService

class MockWeatherService(WeatherService):
    """
    Placeholder weather service for testing purposes.
    Returns fixed weather data regardless of city.
    """

    def get_weather(self, city: str) -> str:
        """
        Returns fake weather info for the given city.
        """
        info = {
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

        return (
            f"{city.title()} Weather (Placeholder):\n"
            f"Temperature: {info['temperature']}°C (feels like {info['apparent_temperature']}°C)\n"
            f"Precipitation probability: {info['precipitation_probability']}%\n"
            f"Visibility: {info['visibility']} m\n"
            f"UV index: {info['uv_index']}\n"
            f"Sunshine duration: {info['sunshine_duration']} s\n"
            f"Humidity: {info['humidity']}%\n"
            f"Dew point: {info['dew_point']}°C\n"
            f"Daytime: {'Yes' if info['is_day'] else 'No'}"
        )
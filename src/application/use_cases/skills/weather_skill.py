"""
WeatherSkill: returns the weather for a given city.
"""

from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.weather_ports import WeatherPort

class WeatherSkill(RobotSkill):
    """
    Handles 'weather' commands. For now, returns a placeholder response.
    """
    def __init__(self, service: WeatherPort):
        self.service = service

    def can_handle(self, command: Command) -> bool:
        return command.get_name() == "weather"

    def handle(self, command: Command) -> CommandResult:
        city = command.get_args().get("text", "unknown location")
        weather_info = self.service.get_weather(city)

        if not weather_info.get("success", False):
            error_message = weather_info.get("message", "Unknown error")
            return CommandResult(success=False, message=f"Could not get weather for '{city}'. Error: {error_message}")

        weather_text = (
            f"{city.title()} Weather:\n"
            f"Temperature: {str(weather_info['temperature'])}°C (feels like {weather_info['apparent_temperature']}°C)\n"
            f"Precipitation probability: {weather_info['precipitation_probability']}%\n"
            f"Visibility: {weather_info['visibility']} m\n"
            f"UV index: {weather_info['uv_index']}\n"
            f"Sunshine duration: {weather_info['sunshine_duration']} s\n"
            f"Humidity: {weather_info['humidity']}%\n"
            f"Dew point: {weather_info['dew_point']}°C\n"
            f"Daytime: {'Yes' if weather_info['is_day'] else 'No'}"
            )

        return CommandResult(success=True, message=weather_text)
"""
WeatherSkill: returns the weather for a given city.
"""

from src.raspberry_friend.model.skill import RobotSkill
from src.raspberry_friend.model.command import Command, CommandResult
from src.raspberry_friend.services.weather_service import WeatherService

class WeatherSkill(RobotSkill):
    """
    Handles 'weather' commands. For now, returns a placeholder response.
    """
    def __init__(self, service: WeatherService):
        self.service = service

    def can_handle(self, command: Command) -> bool:
        return command.name == "weather"

    def handle(self, command: Command) -> CommandResult:
        city = command.args.get("text", "unknown location")
        weather_info = self.service.get_weather(city)
        return CommandResult(success=True, message=weather_info)
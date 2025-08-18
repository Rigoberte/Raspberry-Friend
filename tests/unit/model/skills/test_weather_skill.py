"""
Unit tests for WeatherSkill.
"""

import pytest
from src.raspberry_friend.model.command import Command, CommandResult
from src.raspberry_friend.model.skills.weather_skill import WeatherSkill
from src.raspberry_friend.services.mock_weather_service import MockWeatherService  # placeholder

def test_weather_skill_handles_weather_command_with_supported_city():
    """
    Given a WeatherSkill instance, when it receives a 'weather' command with a supported city,
    it should return a CommandResult containing the weather for that city.
    """
    skill = WeatherSkill(service=MockWeatherService())
    command = Command(name="weather", args={"text": "Buenos Aires"})  # valid city
    
    result: CommandResult = skill.handle(command)

    PLACEHOLDER_TEXT = (
        "Buenos Aires Weather (Placeholder):\n"
        "Temperature: 20.0°C (feels like 19.5°C)\n"
        "Precipitation probability: 10%\n"
        "Visibility: 10000 m\n"
        "UV index: 3\n"
        "Sunshine duration: 3600 s\n"
        "Humidity: 50%\n"
        "Dew point: 10°C\n"
        "Daytime: Yes"
    )
    
    assert isinstance(result, CommandResult)
    assert result.success is True
    assert result.message == PLACEHOLDER_TEXT

def test_weather_skill_cannot_handle_other_commands():
    """
    WeatherSkill should return False for can_handle when the command is not 'weather'.
    """
    skill = WeatherSkill(service=MockWeatherService())
    command = Command(name="echo", args={"text": "Hello"})
    
    assert skill.can_handle(command) is False
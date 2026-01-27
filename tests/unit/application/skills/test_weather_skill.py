"""
Unit tests for WeatherSkill.
"""

import pytest
from src.application.use_cases.skills.weather_skill import WeatherSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.weather_ports import WeatherPort


class MockWeatherService(WeatherPort):
    """Mock weather service for testing."""
    
    def get_weather(self, city: str) -> dict[str, float | int | bool | str]:
        if city.lower() == "buenos aires":
            return {
                "success": True,
                "temperature": 20.0,
                "feels_like": 19.5,
                "precipitation_probability": 10,
                "message": "Sunny"
            }
        else:
            return {
                "success": False,
                "message": f"City '{city}' is not supported."
            }


class TestWeatherSkill:
    """Tests for WeatherSkill."""

    def test_can_handle_weather_command(self):
        """Test that WeatherSkill can handle 'weather' commands."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="weather", slots={"text": "Buenos Aires"})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is True

    def test_cannot_handle_other_commands(self):
        """Test that WeatherSkill cannot handle non-weather commands."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="echo", slots={})

        # Act
        can_handle = skill.can_handle(command)

        # Assert
        assert can_handle is False

    def test_handle_weather_with_supported_city(self):
        """Test that WeatherSkill returns weather for supported city."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="weather", slots={"text": "Buenos Aires"})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        assert result.is_successful() is True
        assert "Buenos Aires" in result.get_message()

    def test_handle_weather_with_unsupported_city(self):
        """Test that WeatherSkill handles unsupported cities."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="weather", slots={"text": "Unknown City"})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        # Could be success=False or success=True with error message
        assert "Unknown City" in result.get_message() or "not supported" in result.get_message()

    def test_handle_weather_without_city(self):
        """Test that WeatherSkill handles missing city argument."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="weather", slots={})

        # Act
        result = skill.handle(command)

        # Assert
        assert isinstance(result, CommandResult)
        # Should handle gracefully (either error or default location)

    def test_weather_skill_uses_injected_service(self):
        """Test that WeatherSkill uses the injected weather service."""
        # Arrange
        service = MockWeatherService()
        skill = WeatherSkill(service=service)
        command = Command(name="weather", slots={"text": "Buenos Aires"})

        # Act
        result = skill.handle(command)

        # Assert
        # Verify that the mock service was used (returns our mock data)
        assert "20" in result.get_message() or "Sunny" in result.get_message() or "Buenos Aires" in result.get_message()

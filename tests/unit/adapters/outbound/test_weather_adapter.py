"""
Unit tests for Weather Adapters.
"""

import pytest
from src.domain.ports.outbound.weather_ports import WeatherPort
from src.adapters.outbound.weather.mock_weather_adapter import MockWeatherPort
from src.adapters.outbound.weather.real_weather_adapter import RealWeatherPort


class TestMockWeatherAdapter:
    """Tests for MockWeatherPort adapter."""

    def test_mock_weather_service_implements_interface(self):
        """Test that MockWeatherPort implements WeatherPort interface."""
        # Arrange & Act
        service = MockWeatherPort()

        # Assert
        assert isinstance(service, WeatherPort)

    def test_mock_weather_returns_weather_for_supported_city(self):
        """Test that mock service returns weather data for supported cities."""
        # Arrange
        service = MockWeatherPort()

        # Act
        result = service.get_weather("Buenos Aires")

        # Assert
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "temperature" in result

    def test_mock_weather_returns_error_for_unsupported_city(self):
        """Test that mock service returns error for unsupported cities."""
        # Arrange
        service = MockWeatherPort()

        # Act
        result = service.get_weather("Unknown City")

        # Assert
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "message" in result


class TestRealWeatherAdapter:
    """Tests for RealWeatherPort adapter."""

    def test_real_weather_service_implements_interface(self):
        """Test that RealWeatherPort implements WeatherPort interface."""
        # Arrange & Act
        service = RealWeatherPort()

        # Assert
        assert isinstance(service, WeatherPort)

    def test_real_weather_returns_dict(self):
        """Test that real service returns a dictionary."""
        # Arrange
        service = RealWeatherPort()

        # Act
        result = service.get_weather("Buenos Aires")

        # Assert
        assert isinstance(result, dict)
        assert "success" in result

    def test_real_weather_handles_unsupported_city(self):
        """Test that real service handles unsupported cities gracefully."""
        # Arrange
        service = RealWeatherPort()

        # Act
        result = service.get_weather("NonExistentCity123")

        # Assert
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "not supported" in result["message"]

    @pytest.mark.integration
    def test_real_weather_api_call(self):
        """Integration test: Real API call for Buenos Aires."""
        # Arrange
        service = RealWeatherPort()

        # Act
        result = service.get_weather("Buenos Aires")

        # Assert
        assert isinstance(result, dict)
        # If city is supported, should have weather data
        if result["success"]:
            assert "temperature" in result or "message" in result

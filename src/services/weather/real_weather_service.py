import requests
from datetime import datetime, timezone
from .weather_service import WeatherService

# Diccionario escalable de ciudades soportadas
CITY_COORDINATES = {
    "buenos aires": {"lat": -34.6131, "lon": -58.3772},
    "ba": {"lat": -34.6131, "lon": -58.3772},
    # Más ciudades se agregan aquí
}

class RealWeatherService(WeatherService):
    """
    Fetches weather from Open-Meteo API for supported cities.
    """
    def __init__(self):
        pass

    def get_weather(self, city: str) -> dict[str, float | int | bool | str]:
        """
        Returns current weather info for a given city using the Open-Meteo API.
        If city is not supported, returns a message indicating that.
        """
        city_key = city.lower()
        if city_key not in CITY_COORDINATES:
            return {
                "success": False,
                "message": f"City '{city}' is not supported."
            }

        coords = CITY_COORDINATES[city_key]
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "hourly": ",".join([
                "temperature_2m",
                "precipitation_probability",
                "apparent_temperature",
                "visibility",
                "uv_index",
                "sunshine_duration",
                "relative_humidity_2m",
                "dew_point_2m",
                "is_day"
            ]),
            "forecast_days": 1
        }

        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()

            # Current UTC hour as aware datetime
            now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            times = data["hourly"]["time"]

            # Find closest hour index, making API times aware UTC
            closest_idx = min(
                range(len(times)),
                key=lambda i: abs(datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc) - now_utc)
            )

            hourly = data["hourly"]
            info = {
                "success": True,
                "message": "Weather fetched successfully.",
                "temperature": hourly["temperature_2m"][closest_idx],
                "apparent_temperature": hourly["apparent_temperature"][closest_idx],
                "precipitation_probability": hourly["precipitation_probability"][closest_idx],
                "visibility": hourly["visibility"][closest_idx],
                "uv_index": hourly["uv_index"][closest_idx],
                "sunshine_duration": hourly["sunshine_duration"][closest_idx],
                "humidity": hourly["relative_humidity_2m"][closest_idx],
                "dew_point": hourly["dew_point_2m"][closest_idx],
                "is_day": bool(hourly["is_day"][closest_idx])
            }

            return info

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching weather data: {str(e)}"
            }
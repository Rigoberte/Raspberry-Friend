import requests
from datetime import datetime, timezone, timedelta
from src.domain.ports.outbound.weather_ports import WeatherPort
from src.adapters.outbound.weather.cities_info_adapter import CitiesInfoAdapter

class RealWeatherPort(WeatherPort):
    """
    Fetches weather from Open-Meteo API for supported cities.
    """
    def __init__(self):
        self.CitiesInfoAdapter = CitiesInfoAdapter()

        self.PARAMS_HOURLY = [
                "temperature_2m",
                "precipitation_probability",
                "apparent_temperature",
                "visibility",
                "uv_index",
                "sunshine_duration",
                "relative_humidity_2m",
                "dew_point_2m",
                "is_day"
            ]

    def get_weather(self, city: str) -> dict[str, float | int | bool | str]:
        """
        Returns current weather info for a given city using the Open-Meteo API.
        If city is not supported, returns a message indicating that.
        """
        likest_city = self.CitiesInfoAdapter.find_best_city(city)
            
        if likest_city: 
            complete_city_name = likest_city.get("complete_city_name") 
        else:
            return {
                "success": False,
                "message": f"City '{city}' not supported."
            }

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": likest_city["latitude"],
            "longitude": likest_city["longitude"],
            "hourly": ",".join(self.PARAMS_HOURLY),
            "forecast_days": 1
        }

        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()

            # Current UTC hour as aware datetime
            now_utc = datetime.now(timezone(timedelta(hours=-3))).replace(minute=0, second=0, microsecond=0)
            times = data["hourly"]["time"]

            # Find closest hour index, making API times aware UTC
            closest_idx = min(
                range(len(times)),
                key=lambda i: abs(datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc) - now_utc)
            )

            hourly = data["hourly"]
            info = {
                "success": True,
                "message": complete_city_name,
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
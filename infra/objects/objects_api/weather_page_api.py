

from infra.objects.data_classes.get_weather_response import WeatherResponse
from infra.utils.api_access import ApiAccess


class WeatherPageApi:
    def __init__(
            self
    ) -> None:
        self.api_access = ApiAccess()
        self.config_manager = ConfigManager()

        self.BASE_URL = self.config_manager.get_api_base_url()
        self.API_KEY = self.config_manager.get_api_key()

    async def get_weather_data_by_city_id(self, city_id: str) -> WeatherResponse:
        # Fetch weather data from API
        weather_url = f"{self.BASE_URL}?id={city_id}&appid={self.API_KEY}&units=metric"
        weather_dict = await ApiAccess.execute_get_request_async(weather_url)

        # Convert to WeatherResponse
        weather_response = WeatherResponse.from_dict(weather_dict)

        # Insert weather data into database
        self.database_helper.insert_weather_data([weather_response])

        return weather_response



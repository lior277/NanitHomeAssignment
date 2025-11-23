
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By

from automation_framework.utilities.web_driver_extension.web_driver_extension import DriverEX
from infra.objects.data_classes.get_weather_response import WeatherResponse


class WeatherPageUi:
    def __init__(self, driver: webdriver) -> None:
        self.driver = driver
        self._auto_complete_city_name = "//li[contains(.,'{name}')]"

        # locators
        self._search_city_input_ext = (By.CSS_SELECTOR, "input[type='search']")
        self._temperatura_ext = (By.CSS_SELECTOR, "div[class='h2']")
        self._feels_like_ext = (By.XPATH, "//div[@id='qlook']//p[contains(text(), 'Feels Like')]")

    def _search_by_city_name(self, city_name: str) -> None:
        search_ext = (By.XPATH, self._auto_complete_city_name.format(name=city_name))
        DriverEX.send_keys_auto(driver=self.driver, by=self._search_city_input_ext,
                                input_text=city_name)

        DriverEX.force_click(driver=self.driver, by=search_ext)

    async def get_temperatura_data_by_city_name(self, city_name: str) -> WeatherResponse:
        self._search_by_city_name(city_name)
        temperatura_text = DriverEX.search_element(driver=self.driver, by=self._temperatura_ext).text
        temperatura = temperatura_text.split('°')[0].strip()
        feels_like_text = DriverEX.search_element(driver=self.driver, by=self._feels_like_ext).text
        feels_like = feels_like_text.split(":")[1].strip()
        feels_like = feels_like.split('°')[0].strip()
        temp_min = 0.0
        temp_max = 0.0

        return WeatherResponse(
            city_name=city_name,
            temperature=temperatura,
            feels_like=feels_like,
            temp_min=temp_min,
            temp_max=temp_max
        )








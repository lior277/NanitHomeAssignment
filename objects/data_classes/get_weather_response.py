from dataclasses import dataclass
from typing import Optional

@dataclass
class WeatherResponse:
   city_name: str
   temperature: str
   feels_like: str
   temp_min: float
   temp_max: float
   average_temperature: Optional[float] = None

   @classmethod
   def from_dict(cls, data: dict):
       return cls(
           city_name=data.get('name', ''),
           temperature=data['main'].get('temp', 0.0),
           feels_like=data['main'].get('feels_like', 0.0),
           temp_min=data['main'].get('temp_min', 0.0),
           temp_max=data['main'].get('temp_max', 0.0),
           average_temperature=(data['main'].get('temp_min', 0.0) + data['main'].get('temp_max', 0.0)) / 2
       )
# coding: utf-8
"""Tests Météo-France module. Forecast class."""
from unittest.mock import Mock

import pytest
import requests

from meteofrance_api import MeteoFranceClient
from meteofrance_api.const import METEOFRANCE_API_URL

def test_rain() -> None:
    """Test rain forecast on a covered zone."""
    client = MeteoFranceClient()

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)

    assert isinstance(rain.update_time, str)
    assert isinstance(rain.geometry, dict)
    assert isinstance(rain.properties, dict)
    assert "rain_intensity" in rain.forecast[0].keys()


def test_rain_not_covered() -> None:
    """Test rain forecast result on a non covered zone."""
    client = MeteoFranceClient()

    with pytest.raises(requests.HTTPError, match=r"400 .*"):
        client.get_rain(latitude=45.508, longitude=-73.58)


def test_rain_expected(requests_mock: Mock) -> None:
    """Test datecomputation when rain is expected within the hour."""
    client = MeteoFranceClient()

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json={
            "update_time":"2024-02-04T13:55:00.000Z",
            "type":"Feature",
            "geometry":{
                "type":"Point",
                "coordinates":[2.239895,48.807166]
            },
            "properties":{
                "altitude":76,
                "name":"Meudon",
                "country":"FR - France",
                "french_department":"92",
                "rain_product_available":1,
                "timezone":"Europe/Paris",
                "forecast": [
                    {"time":"2024-02-04T14:10:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:15:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:20:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:25:00.000Z","rain_intensity":2,"rain_intensity_description":"Pluie faible"},
                    {"time":"2024-02-04T14:30:00.000Z","rain_intensity":3,"rain_intensity_description":"Pluie modérée"},
                    {"time":"2024-02-04T14:35:00.000Z","rain_intensity":2,"rain_intensity_description":"Pluie faible"},
                    {"time":"2024-02-04T14:45:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:55:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T15:05:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                ],
            }
        },
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    date_rain = rain.next_rain_date_locale()
    assert str(date_rain) == "2020-05-20 19:50:00+02:00"
    assert (
        str(rain.timestamp_to_locale_time(rain.forecast[3]["dt"]))
        == "2020-05-20 19:50:00+02:00"
    )


def test_no_rain_expected(requests_mock: Mock) -> None:
    """Test datecomputation when rain is expected within the hour."""
    client = MeteoFranceClient()

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json={
            "update_time":"2024-02-04T13:55:00.000Z",
            "type":"Feature",
            "geometry":{
                "type":"Point",
                "coordinates":[2.239895,48.807166]
            },
            "properties":{
                "altitude":76,
                "name":"Meudon",
                "country":"FR - France",
                "french_department":"92",
                "rain_product_available":1,
                "timezone":"Europe/Paris",
                "forecast": [
                    {"time":"2024-02-04T14:10:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:15:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:20:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:25:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:30:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:35:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:45:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T14:55:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                    {"time":"2024-02-04T15:05:00.000Z","rain_intensity":1,"rain_intensity_description":"Temps sec"},
                ],
            }
        },
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    assert rain.next_rain_date_locale() is None

# -*- coding: utf-8 -*-
"""Rain in the next hour Python model for the Météo-France REST API."""
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

from meteofrance_api.helpers import timestamp_to_dateime_with_locale_tz

class RainData(TypedDict):
    """Describing the data structure of rain object returned by the REST API."""

    position: Dict[str, Any]
    updated_on: int
    forecast: List[Dict[str, Any]]
    quality: int


class Rain:
    """Class to access the results of 'rain' REST API request.

    Attributes:
        position: A dictionary with metadata about the position of the forecast place.
        updated_on:  A timestamp as int corresponding to the latest update date.
        forecast: A list of dictionaries to describe the following next hour rain
            forecast.
        quality: An integer. Don't know yet the usage.
    """

    def __init__(self, raw_data: RainData) -> None:
        """Initialize a Rain object.

        Args:
            raw_data: A dictionary representing the JSON response from 'rain' REST API
                request. The structure is described by the RainData class.
        """
        self.raw_data = raw_data

    @property
    def position(self) -> Dict[str, Any]:
        """Return the position information of the rain forecast."""

        """ Convert new v2 format to original one """
        lon, lat = self.raw_data["geometry"]["coordinates"]
        alti = self.raw_data["properties"]["altitude"]
        name = self.raw_data["properties"]["name"]
        country = self.raw_data["properties"]["country"]
        dept = self.raw_data["properties"]["french_department"]
        rain_product_available = 1
        timezone = self.raw_data["properties"]["timezone"]

        # Construct the original format
        position = {
            "lat": lat,
            "lon": lon,
            "alti": alti,
            "name": name,
            "country": country,
            "dept": dept,
            "rain_product_available": rain_product_available,
            "timezone": timezone
        }

        return position

    @property
    def updated_on(self) -> int:
        """Return the update timestamp of the rain forecast."""
        
        """ Convert new v2 format to original one """
        time_iso8601 = self.raw_data["update_time"]
        timestamp = datetime.fromisoformat(time_iso8601.replace('Z', '+00:00')).timestamp()
        return int(timestamp)
    
    @property
    def forecast(self) -> List[Dict[str, Any]]:
        """Return the rain forecast."""
        forecast: List[Dict[str, Any]] = []

        """ Convert new v2 format to original one """
        for item in self.raw_data["properties"]["forecast"]:
            time_iso8601 = item['time']
            rain_intensity = item['rain_intensity']
            rain_intensity_description = item['rain_intensity_description']

            # Convert ISO 8601 formatted time to Unix timestamp
            timestamp = datetime.fromisoformat(time_iso8601.replace('Z', '+00:00')).timestamp()

            # Construct the original format
            new_item = {
                "dt": int(timestamp),
                "rain": rain_intensity,
                "desc": rain_intensity_description
            }

            forecast.append(new_item)

        return forecast

    @property
    def quality(self) -> int:
        """Return the quality of the rain forecast: deprecated"""
        # TODO: don't know yet what is the usage
        return 0

    def next_rain_date_locale(self) -> Optional[datetime]:
        """Estimate the date of the next rain in the Place timezone (Helper).

        Returns:
            A datetime instance representing the date estimation of the next rain within
            the next hour.
            If no rain is expected in the following hour 'None' is returned.

            The datetime use the location timezone.
        """
        # search first cadran with rain
        next_rain = next(
            (cadran for cadran in self.forecast if cadran["rain"] > 1), None
        )

        next_rain_dt_local: Optional[datetime] = None
        if next_rain is not None:
            # get the time stamp of the first cadran with rain
            next_rain_timestamp = next_rain["dt"]
            # convert timestamp in datetime with local timezone
            next_rain_dt_local = timestamp_to_dateime_with_locale_tz(
                next_rain_timestamp, self.position["timezone"]
            )

        return next_rain_dt_local

    def timestamp_to_locale_time(self, timestamp: int) -> datetime:
        """Convert timestamp in datetime with rain forecast location timezone (Helper).

        Args:
            timestamp: An integer representing the UNIX timestamp.

        Returns:
            A datetime instance corresponding to the timestamp with the timezone of the
                rain forecast location.
        """
        return timestamp_to_dateime_with_locale_tz(timestamp, self.position["timezone"])

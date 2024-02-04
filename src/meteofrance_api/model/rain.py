# -*- coding: utf-8 -*-
"""Rain in the next hour Python model for the Météo-France REST API."""
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

from meteofrance_api.helpers import time_to_datetime_with_locale_tz

class RainData(TypedDict):
    """Describing the data structure of rain object returned by the REST API."""

    geometry: Dict[str, Any]
    update_time: int
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
    def update_time(self) -> int:
        """Return the update time of the rain forecast."""
        return self.raw_data["update_time"]

    @property
    def geometry(self) -> Dict[str, Any]:
        """Return the geometry information of the rain forecast."""
        return self.raw_data["geometry"]

    @property
    def properties(self) -> List[Dict[str, Any]]:
        """Return the rain properties."""
        return self.raw_data["properties"]

    @property
    def forecast(self) -> List[Dict[str, Any]]:
        """Return the rain forecast."""
        return self.raw_data["properties"]["forecast"]

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
            (cadran for cadran in self.forecast if cadran["rain_intensity"] > 1), None
        )

        next_rain_dt_local: Optional[datetime] = None
        if next_rain is not None:
            # get the time of the first cadran with rain
            next_rain_timestamp = next_rain["time"]
            # convert time in datetime with local timezone
            next_rain_dt_local = time_to_datetime_with_locale_tz(
                next_rain_timestamp, self.properties["timezone"]
            )

        return next_rain_dt_local

    def time_to_locale_time(self, time: str) -> datetime:
        """Convert time in datetime with rain forecast location timezone (Helper).

        Args:
            time: An String representing the UNIX timestamp.

        Returns:
            A datetime instance corresponding to the timestamp with the timezone of the
                rain forecast location.
        """
        return time_to_datetime_with_locale_tz(time, self.properties["timezone"])

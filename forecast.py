import argparse
import logging
import os
import sys
from datetime import datetime

import requests


class EmptyDatabaseError(Exception):
    """A custom exception of a Forecast class"""


class InvalidCityNameError(Exception):
    """A custom exception of a Forecast class"""


class Forecast:
    """A class used to represent an hourly forecast for a given city

    ...

    Attributes
    -------
    API_KEY : str
        An individual key used to access API
    CITY_SEARCH_URL : str
        A URL used for looking up a city
    FORECAST_URL : str
        A URL used for looking up an hourly forecast for a city
    DEGREE_SIGN : str
        A degree sign
    city : str
        A name of a city

    Methods
    -------
    get_location_key()
        Gets a location key based on a city name
    get_forecast()
        Gets an hourly forecast based on a location key

    Raises
    ------
    EmptyDatabaseError
        An exception raised when a city does not exist in the database
    InvalidCityNameError
        An exception raised when a city name is not a string
    """

    API_KEY = os.environ.get("API_KEY")
    CITY_SEARCH_URL = "http://dataservice.accuweather.com/locations/v1/cities/search/"
    FORECAST_URL = "http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/"
    DEGREE_SIGN = "\N{DEGREE SIGN}"

    def __init__(self, city: str):
        """
        Parameters
        ----------
        city : str
            A name of a city
        """
        self.city = city

    def get_location_key(self) -> str | None:
        """
        Gets a location key based on a city name

        Returns
        -------
        str | None
            A location key

        Raises
        ------
        EmptyDatabaseError
            An exception raised when a city does not exist in the database
        InvalidCityNameError
            An exception raised when a city name is not a string
        """

        r = requests.get(
            self.CITY_SEARCH_URL, params={"apikey": self.API_KEY, "q": self.city}
        )
        try:
            if not self.city.isalpha():
                raise InvalidCityNameError("City name must be a string.")
            r.raise_for_status()
            r = r.json()
            if not r:
                raise EmptyDatabaseError("There is no match in the database.")
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e.args[0]}")
            sys.exit()
        location_key = r[0]["Key"]
        return location_key

    def get_forecast(self) -> None:
        """Gets an hourly forecast based on a location key"""

        location_key = self.get_location_key()
        r = requests.get(
            f"{self.FORECAST_URL}{location_key}",
            params={"apikey": self.API_KEY, "metric": "true"},
        )
        try:
            r.raise_for_status()
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e.args[0]}")
            sys.exit()
        r = r.json()
        date = r[0]["DateTime"][:10]
        temp = r[0]["Temperature"]["Value"]
        date = datetime.strftime(datetime.strptime(date, "%Y-%m-%d"), "%d.%m.%Y")
        logging.info(f"Date: {date}, Temperature: {temp}{self.DEGREE_SIGN}C")


def main():
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser(description="A weather app")
    parser.add_argument(
        "city",
        nargs=1,
        metavar="city",
        type=str,
        help="Returns forecast data for the next hour for a specific location.",
    )
    args = parser.parse_args()
    if len(args.city) != 0:
        forecast = Forecast(*args.city)
        forecast.get_forecast()


if __name__ == "__main__":
    main()

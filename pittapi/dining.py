"""
The Pitt API, to access workable data of the University of Pittsburgh
Copyright (C) 2015 Ritwik Gupta

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import requests
from datetime import datetime
from typing import Any

JSON = dict[str, Any]

REQUEST_HEADERS = {"User-Agent": "Chrome/103.0.5026.0"}

LOCATIONS = {
    "ETHEL'S",
    "THE EATERY",
    "PANERA BREAD",
    "TRUE BURGER",
    "THE PERCH",
    "FORBES STREET MARKET",
    "BUNSEN BREWER",
    "WICKED PIE",
    "SMOKELAND BBQ AT THE PETERSEN EVENTS CENTER",
    "THE MARKET AT TOWERS",
    "THE DELICATESSEN",
    "CAMPUS COFFEE & TEA CO - TOWERS",
    "PA TACO CO.",
    "FT. PITT SUBS",
    "CREATE",
    "POM & HONEY",
    "THE ROOST",
    "CATHEDRAL SUSHI",
    "BURRITO BOWL",
    "CHICK-FIL-A",
    "SHAKE SMART",
    "STEEL CITY KITCHEN",
    "SMOKELAND BBQ FOOD TRUCK",
    "CAMPUS COFFEE & TEA CO - SUTHERLAND",
    "THE MARKET AT SUTHERLAND",
    "PLATE TO PLATE AT SUTHERLAND MARKET",
    "EINSTEIN BROS. BAGELS - POSVAR",
    "EINSTEIN BROS. BAGELS - BENEDUM",
    "BOTTOM LINE BISTRO",
    "CAFE VICTORIA",
    "CAFE 1787",
    "CAMPUS COFFEE & TEA CO - PUBLIC HEALTH",
    "RXPRESSO",
    "SIDEBAR CAFE",
    "CAFE 1923",
}

LOCATIONS_URL = "https://api.dineoncampus.com/v1/locations/status?site_id=5e6fcc641ca48e0cacd93b04&platform="
HOURS_URL = "https://api.dineoncampus.com/v1/locations/weekly_schedule?site_id=5e6fcc641ca48e0cacd93b04&date=%22{date_str}%22"
PERIODS_URL = "https://api.dineoncampus.com/v1/location/{location_id}/periods?platform=0&date={date_str}"
MENU_URL = "https://api.dineoncampus.com/v1/location/{location_id}/periods/{period_id}?platform=0&date={date_str}"


def get_locations() -> dict[str, JSON]:
    """Gets data about all dining locations"""
    resp = requests.get(LOCATIONS_URL, headers=REQUEST_HEADERS)
    locations = resp.json()["locations"]
    dining_locations = {location["name"].upper(): location for location in locations}

    return dining_locations


def get_location_hours(location_name: str | None = None, date: datetime | None = None) -> dict[str, list[dict[str, int]]]:
    """Returns dictionary containing Opening and Closing times of locations open on date.
    - Ex:{'The Eatery': [{'start_hour': 7, 'start_minutes': 0, 'end_hour': 0, 'end_minutes': 0}]}
    - if location_name is None, returns times for all locations
    - date must be in YYYY,MM,DD format, will return data on current day if None
    """

    if location_name is not None:
        location_name = location_name.upper()
        if location_name not in LOCATIONS:
            raise ValueError("Invalid Dining Location")

    if date is None:
        date = datetime.now()

    date_str = date.strftime("%Y-%m-%d")
    resp = requests.get(
        HOURS_URL.format(date_str=date_str),
        headers=REQUEST_HEADERS,
    )

    if resp.status_code == 502:
        raise ValueError("Invalid Date")

    locations = resp.json()["the_locations"]

    if location_name is None:
        hours = {
            location["name"]: day["hours"] for location in locations for day in location["week"] if day["date"] == date_str
        }
        return hours

    for location in locations:
        if location["name"].upper() == location_name:
            hours = {location["name"]: day["hours"] for day in location["week"] if day["date"] == date_str}
            return hours

    return {}


def get_location_menu(location: str, date: datetime | None = None, period_name: str | None = None) -> JSON:
    """Returns menu data for given dining location on given day/period
    - period_name used for locations with different serving periods(i.e. 'Breakfast','Lunch','Dinner','Late Night')
    - None -> Returns menu for first(or only) period at location
    """
    location = location.upper()
    if location not in LOCATIONS:
        raise ValueError("Invalid Dining Location")

    if date is None:
        date = datetime.today()
    if period_name is not None:
        period_name = period_name.lower()

    date_str = date.strftime("%y-%m-%d")
    location_id = get_locations()[location]["id"]
    periods_resp = requests.get(
        PERIODS_URL.format(location_id=location_id, date_str=date_str),
        headers=REQUEST_HEADERS,
    )

    if periods_resp.status_code == 502:
        raise ValueError("Invalid Date")

    periods = periods_resp.json()["periods"]
    if period_name is None or len(periods) == 1:
        period_id = periods[0]["id"]
    else:
        for period in periods:
            if period["name"].lower() == period_name:
                period_id = period["id"]

    menu_resp = requests.get(
        MENU_URL.format(location_id=location_id, period_id=period_id, date_str=date_str),
        headers=REQUEST_HEADERS,
    )
    menu: JSON = menu_resp.json()["menu"]

    return menu

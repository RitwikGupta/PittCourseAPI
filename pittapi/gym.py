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

from __future__ import annotations

from bs4 import BeautifulSoup
import requests
from typing import NamedTuple

GYM_URL = "https://connect2concepts.com/connect2/?type=bar&key=17c2cbcb-ec92-4178-a5f5-c4860330aea0"

GYM_NAMES = [
    "Baierl Rec Center",
    "Bellefield Hall: Fitness Center & Weight Room",
    "Bellefield Hall: Court & Dance Studio",
    "Trees Hall: Fitness Center",
    "Trees Hall: Courts",
    "Trees Hall: Racquetball Courts & Multipurpose Room",
    "William Pitt Union",
    "Pitt Sports Dome",
]


class Gym(NamedTuple):
    name: str
    date: str
    count: int
    percentage: int

    @classmethod
    def from_text(cls, text: str) -> Gym:
        info = text.split("|")
        name = info[0]
        if len(info) < 4:
            return cls(name=name, date=None, count=None, percentage=None)
        count = int(info[2][12:])
        date = info[3][9:]
        try:
            percentage = int(info[4].rstrip("%"))
        except ValueError:
            percentage = 0

        return cls(name=name, date=date, count=count, percentage=percentage)


def get_all_gyms_info() -> list[Gym]:
    """Fetches list of Gym named tuples with all gym information"""
    # Was getting a Mod Security Error
    # Fix: https://stackoverflow.com/questions/61968521/python-web-scraping-request-errormod-security
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
    }

    page = requests.get(GYM_URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    gym_info_list = soup.find_all("div", class_="barChart")

    # Iterate through list and add to dictionary
    gyms = [Gym.from_text(gym.get_text("|", strip=True)) for gym in gym_info_list]
    return gyms


def get_gym_info(gym_name: str) -> Gym | None:
    """Fetches the information of a singular gym as a tuple"""
    info = get_all_gyms_info()
    if gym_name in GYM_NAMES:
        for gym in info:
            if gym.name == gym_name and gym.date and gym.count and gym.percentage:
                return gym
    return None

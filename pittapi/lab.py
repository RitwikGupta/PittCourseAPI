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

from typing import List, NamedTuple

from requests_html import HTMLSession
from parse import compile
import requests
import urllib3

LABS_URL = "https://pitt-keyserve-prod.univ.pitt.edu/maps/std/avail.json"
HILLMAN_URL = "https://pitt.libcal.com/spaces/bookings/search?lid=917&gid=1558&eid=0&seat=0&d=1&customDate=&q=&daily=0&draw=1&order%5B0%5D%5Bcolumn%5D=1&order%5B0%5D%5Bdir%5D=asc&start=0&length=25&search%5Bvalue%5D=&_=1717907260661"

"""
Lab API is insecure for some reason (it's official Pitt one
so no concern), just doing this to supress warnings

Lab API now supports some additional features, supporting some aspects of fetching Hillman data, such as reserved times
and total amount of reservations
"""

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
LAB_OPEN_PATTERN = compile(
    "{name} Lab is {status}: {windows:d} Windows, {macs:d} Macs, {linux:d} Linux"
)
LAB_CLOSED_PATTERN = compile("{name} Lab is currently {status}")


class Lab(NamedTuple):
    name: str
    status: str
    windows: int
    mac: int
    linux: int
"""

def _fetch_labs():
    """Fetches dictionary of status of all labs."""
    labs = {}

    # get the full lab data from API
    resp = requests.get(LABS_URL, verify=False)
    resp = resp.json()
    data = resp["results"]["states"]

    # "1" means open, "0" means closed
    for location in data:
        labs[location] = data[location]["state"]

    return labs


def get_lab_status():
    """Returns a list with status and amount of open machines."""
    # get the list of all the labs (plus open status) at other
    statuses = []
    labs = _fetch_labs()

    # get all the different labs + printers at all Pitt campuses
    resp = requests.get(LABS_URL, verify=False)
    resp = resp.json()
    data = resp["results"]["divs"]

    for key in data:
        # only include those that are Pitt main campus
        if key["name"] in labs:
            total = key["total"]
            in_use = key["active"]
            statuses.append(
                {
                    "location": key["name"],
                    "isOpen": labs[key["name"]],
                    "total": total,
                    "in_use": in_use
                }
            )
    return statuses


def hillman_total_reserved():
    """Returns a simple count dictionary of the total amount of reserved rooms appointments"""
    count = {}
    resp = requests.get(HILLMAN_URL)
    resp = resp.json()
    total_records = resp["recordsTotal"]

    count["Total Hillman Reservations"] = total_records
    return count


def reserved_hillman_times():
    """Returns a dictionary with of reserved rooms of the Hillman with their respective times"""
    bookings = {}

    resp = requests.get(HILLMAN_URL)
    resp = resp.json()
    data = resp["data"]

    if data is None:
        return bookings

    for reservation in data:
        from_time = reservation["from"]
        to_time = reservation["to"]
        roomName = reservation["itemName"]
        bookings[roomName] = [from_time, to_time]

    return bookings
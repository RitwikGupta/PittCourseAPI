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

import requests
from typing import Any


BASE_URL = "https://www.laundryview.com/api/currentRoomData?school_desc_key=197&location={location}"

LOCATION_LOOKUP = {
    "TOWERS": "2430136",
    "BRACKENRIDGE": "2430119",
    "HOLLAND": "2430137",
    "LOTHROP": "2430151",
    "MCCORMICK": "2430120",
    "SUTH_EAST": "2430135",
    "SUTH_WEST": "2430134",
    "FORBES_CRAIG": "2430142",
}


def _get_laundry_info(building_name: str) -> Any:
    """Returns JSON object of laundry view webpage"""
    building_name = building_name.upper()
    url = BASE_URL.format(location=LOCATION_LOOKUP[building_name])
    response = requests.get(url)
    info = response.json()
    return info


def get_status_simple(building_name: str) -> dict[str, str]:
    """
    :returns: a dictionary with free washers and dryers as well as total washers
              and dryers for given building

    :param: loc: Building name, case doesn't matter
        -> TOWERS
        -> BRACKENRIDGE
        -> HOLLAND
        -> LOTHROP
        -> MCCORMICK
        -> SUTH_EAST
        -> SUTH_WEST
    """
    laundry_info = _get_laundry_info(building_name)
    freeWashers, freeDryers, totalWashers, totalDryers = 0, 0, 0, 0

    for obj in laundry_info["objects"]:
        if obj["type"] == "washFL":
            totalWashers += 1
            if obj["status_toggle"] == 0:
                freeWashers += 1
        elif obj["type"] == "dry":
            totalDryers += 1
            if obj["status_toggle"] == 0:
                freeDryers += 1
        # for towers, they have "combo" machines with this type, no individual washers and dryers |
        # one part of combo being in use marks the whole thing as in use, so we can only show if
        # both parts are free.
        elif obj["type"] == "washNdry":
            totalWashers += 1
            totalDryers += 1
            if obj["status_toggle"] == 0:
                freeDryers += 1
                freeWashers += 1
    return {
        "building": building_name,
        "free_washers": freeWashers,
        "total_washers": totalWashers,
        "free_dryers": freeDryers,
        "total_dryers": totalDryers,
    }


def get_status_detailed(building_name: str) -> list[dict[str, str | int]]:
    """
    :returns: A list of washers and dryers for the passed
              building location with their statuses

    :param building_name: (String) one of these:
        -> BRACKENRIDGE
        -> HOLLAND
        -> LOTHROP
        -> MCCORMICK
        -> SUTH_EAST
        -> SUTH_WEST
    """
    machines = []
    machine_type = "Unknown"
    laundry_info = _get_laundry_info(building_name)

    for obj in laundry_info["objects"]:
        if obj["type"] == "dry":
            machine_type = "dryer"
        elif obj["type"] == "washFL":
            machine_type = "washer"
        elif obj["type"] == "washNDry":
            machine_type = "washAndDry"

        machine_id = obj["appliance_desc_key"]
        machine_status = obj["time_left_lite"]
        time_left = obj["time_remaining"]

        machines.append(
            {
                "machine_id": machine_id,
                "machine_status": machine_status,
                "machine_type": machine_type,
                "time_left": time_left,
            }
        )

    return machines

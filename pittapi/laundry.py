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
from typing import Any, NamedTuple


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


class BuildingStatus(NamedTuple):
    building: str
    free_washers: int
    total_washers: int
    free_dryers: int
    total_dryers: int


class LaundryMachine(NamedTuple):
    id: str
    status: str
    type: str
    time_left: int | None


def _get_laundry_info(building_name: str) -> dict[str, Any]:
    """Returns JSON object of laundry view webpage"""
    building_name = building_name.upper()
    url = BASE_URL.format(location=LOCATION_LOOKUP[building_name])
    response = requests.get(url)
    info: dict[str, Any] = response.json()
    return info


def get_building_status(building_name: str) -> BuildingStatus:
    """
    :returns: a BuildingStatus object with free washers and dryers as well as total washers and dryers for given building

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
    free_washers, free_dryers, total_washers, total_dryers = 0, 0, 0, 0

    for obj in laundry_info["objects"]:
        if obj["type"] == "washFL":
            total_washers += 1
            if obj["status_toggle"] == 0:
                free_washers += 1
        elif obj["type"] == "dry":
            total_dryers += 1
            if obj["status_toggle"] == 0:
                free_dryers += 1
        # The JSON objects provide two separate statuses for combo machines, one for the washer and one for the dryer
        # See tests/samples/laundry_mock_response_towers.json for examples
        #
        # This elif marks a whole combo machine as free if one part is free
        # TODO: rewrite elif to use the separate combo statuses to more accurately count washers and dryers
        # Must first figure out which JSON fields correspond to the washer and which correspond to the dryer
        elif obj["type"] == "washNdry":
            total_washers += 1
            total_dryers += 1
            if obj["status_toggle"] == 0:
                free_dryers += 1
                free_washers += 1
    return BuildingStatus(
        building=building_name,
        free_washers=free_washers,
        total_washers=total_washers,
        free_dryers=free_dryers,
        total_dryers=total_dryers,
    )


def get_laundry_machine_statuses(building_name: str) -> list[LaundryMachine]:
    """
    :returns: A list of washers and dryers for the passed building location with their statuses

    :param building_name: (String) one of these:
        -> BRACKENRIDGE
        -> HOLLAND
        -> LOTHROP
        -> MCCORMICK
        -> SUTH_EAST
        -> SUTH_WEST
    """
    machines = []
    laundry_info = _get_laundry_info(building_name)

    for obj in laundry_info["objects"]:
        if obj["type"] == "dry":
            machine_type = "dryer"
        elif obj["type"] == "washFL":
            machine_type = "washer"
        # TODO: rewrite elif to add two LaundryMachines for combo machines, one for the washer and one for the dryer
        # Must first figure out which JSON fields correspond to the washer and which correspond to the dryer
        elif obj["type"] == "washNdry":
            machine_type = "combo"
        # Skip any JSON object that's not a laundry machine (e.g., card reader)
        else:
            continue

        machine_id = obj["appliance_desc_key"]
        # Possible machine statuses:
        # status_toggle = 0: "Available"
        # status_toggle = 1: TODO, unknown and must be documented, probably "Completed"
        # status_toggle = 2: either "N min remaining" or "Ext. Cycle"
        # status_toggle = 3: "Out of service"
        # status_toggle = 4: "Offline"
        machine_status = obj["time_left_lite"]
        unavailable = machine_status in ("Out of service", "Offline")
        time_left = None if unavailable else obj["time_remaining"]

        machines.append(
            LaundryMachine(
                id=machine_id,
                status=machine_status,
                type=machine_type,
                time_left=time_left,
            )
        )

    return machines

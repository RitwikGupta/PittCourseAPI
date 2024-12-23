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

import re
import requests
from typing import Any, NamedTuple

JSON = dict[str, Any]


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

NUMBER_REGEX = re.compile(r"\d+")


class BuildingStatus(NamedTuple):
    building: str
    free_washers: int
    total_washers: int
    free_dryers: int
    total_dryers: int


class LaundryMachine(NamedTuple):
    name: str
    id: str
    status: str
    type: str
    time_left: int | None


def _get_laundry_info(building_name: str) -> JSON:
    """Returns JSON object of laundry view webpage"""
    building_name = building_name.upper()
    url = BASE_URL.format(location=LOCATION_LOOKUP[building_name])
    response = requests.get(url)
    info: dict[str, Any] = response.json()
    return info


def _parse_laundry_object_json(json: JSON) -> list[LaundryMachine]:
    """
    Parse the given JSON object into a list of laundry machines.
    Returns a list because a single machine may have multiple components
    (one washer and one dryer, two washers, or two dryers).

    Implementation detail: the machine type is determined by checking the "type" JSON field.
    While it'd be more straightforward to check the "combo" boolean field, this field won't exist if the JSON object doesn't
    represent a laundry machine (e.g., a card reader).

    Possible machine statuses:
    status_toggle = 0: "Available"
    status_toggle = 1: "Idle" (finished running)
    status_toggle = 2: either "N min remaining" or "Ext. Cycle" (currently running)
    status_toggle = 3: "Out of service"
    status_toggle = 4: "Offline"
    """
    if json["type"] == "washNdry":  # Combo machine, add washer and dryer separately
        # Only Towers and Lothrop have combo machines, and for those buildings,
        # washers are named with even numbers while dryers are named with odd numbers
        machine1_name = json["appliance_desc"]
        machine1_num_match = NUMBER_REGEX.search(machine1_name)
        if not machine1_num_match:
            raise ValueError(
                f"Found a combo machine with an invalid machine name: {machine1_name}"
            )
        machine1_num = int(machine1_num_match.group(0))
        machine1_type = "washer" if machine1_num % 2 == 0 else "dryer"
        machine1_id = json["appliance_desc_key"]
        machine1_status = json["time_left_lite"]
        unavailable1 = machine1_status in ("Out of service", "Offline")
        time_left1 = None if unavailable1 else json["time_remaining"]

        machine2_name = json["appliance_desc2"]
        machine2_num_match = NUMBER_REGEX.search(machine2_name)
        if not machine2_num_match:
            raise ValueError(
                f"Found a combo machine with an invalid machine name: {machine2_name}"
            )
        machine2_num = int(machine2_num_match.group(0))
        machine2_type = "washer" if machine2_num % 2 == 0 else "dryer"
        machine2_id = json["appliance_desc_key2"]
        machine2_status = json["time_left_lite2"]
        unavailable2 = machine2_status in ("Out of service", "Offline")
        time_left2 = None if unavailable2 else json["time_remaining2"]

        return [
            LaundryMachine(
                name=machine1_name,
                id=machine1_id,
                status=machine1_status,
                type=machine1_type,
                time_left=time_left1,
            ),
            LaundryMachine(
                name=machine2_name,
                id=machine2_id,
                status=machine2_status,
                type=machine2_type,
                time_left=time_left2,
            ),
        ]
    elif json["type"] in ("washFL", "dry"):  # Only washers/only dryers
        machine_type = "washer" if json["type"] == "washFL" else "dryer"
        machine_name = json["appliance_desc"]
        machine_id = json["appliance_desc_key"]
        machine_status = json["time_left_lite"]
        unavailable = machine_status in ("Out of service", "Offline")
        time_left = None if unavailable else json["time_remaining"]
        machines = [
            LaundryMachine(
                name=machine_name,
                id=machine_id,
                status=machine_status,
                type=machine_type,
                time_left=time_left,
            )
        ]

        if (
            "type2" in json
        ):  # Double machine (two washers/two dryers), add second component separately
            machine_type = "washer" if json["type2"] == "washFL" else "dryer"
            machine_name = json["appliance_desc2"]
            machine_id = json["appliance_desc_key2"]
            machine_status = json["time_left_lite2"]
            unavailable = machine_status in ("Out of service", "Offline")
            time_left = None if unavailable else json["time_remaining2"]
            machines.append(
                LaundryMachine(
                    name=machine_name,
                    id=machine_id,
                    status=machine_status,
                    type=machine_type,
                    time_left=time_left,
                )
            )

        return machines
    return []  # Not a laundry machine (card reader, table, etc.)


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
    machines = get_laundry_machine_statuses(building_name)
    free_washers, free_dryers, total_washers, total_dryers = 0, 0, 0, 0
    for machine in machines:
        if machine.type == "washer":
            total_washers += 1
            if machine.status == "Available":
                free_washers += 1
        elif machine.type == "dryer":
            total_dryers += 1
            if machine.status == "Available":
                free_dryers += 1
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
        obj_machines = _parse_laundry_object_json(obj)
        machines.extend(obj_machines)

    return machines

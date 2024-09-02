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

from typing import NamedTuple
import requests

# Suppress ssl warning
import urllib3

urllib3.disable_warnings()

PITT_BASE_URL = "https://pitt-keyserve-prod.univ.pitt.edu/maps/std/"

# Manually pulled from https://pitt-keyserve-prod.univ.pitt.edu/maps/std/avail.json
# Will need to change to pull these dynamically in the future if these IDs change
AVAIL_LAB_ID_MAP = {
    "BELLEFIELD": "bba4a8796295ff6a8df116524b40e178",
    "LAWRENCE": "98a4759fc02ca3655d56cd58abed4e90",
    "SUTH": "8adaaeb974aa38b2283c73532c095ca7",
    "CATH_G27": "6fd5a4e0dd0a32e3ccb441e25a1a2d78",
    "CATH_G62": "04853e8d1453c90a910a0b803529a3a0",
    "BENEDUM": "25d1bfa80cafb622994b7d06c63011f2",
}


class Lab(NamedTuple):
    name: str
    status: bool
    available_computers: int
    off_computers: int
    in_use_computers: int
    out_of_service_computers: int
    total_computers: int


class LabAPIError(Exception):
    """Raised when an error occurs while accessing the Lab API."""

    def __init__(self, message: str):
        super().__init__(message)


def get_one_lab_data(lab_name: str) -> Lab:
    """Fetches text of status/machines of a single lab.

    Args:
        name (str): The name of the lab to fetch data for.
        Valid options: "BELLEFIELD", "LAWRENCE", "SUTH", "CATH_G27", "CATH_G62", "BENEDUM"

    Raises:
        ValueError: If an invalid `id` is provided.

    Returns:
        Lab: A Lab object with the data.
    """

    if lab_name not in AVAIL_LAB_ID_MAP.keys():
        # Dicts are guaranteed to preserve insertion order as of Python 3.7,
        # so the list of valid options will always be printed in the same order
        raise ValueError(f"Invalid lab name: {lab_name}. Valid options: {', '.join(AVAIL_LAB_ID_MAP.keys())}")

    req = requests.get(
        PITT_BASE_URL + AVAIL_LAB_ID_MAP[lab_name] + "/status.json?noredir=1",
        verify=False,
    )

    if req.status_code == 404:
        raise LabAPIError("The Lab ID was invalid. Please open a GitHub issue so we can resolve this.")
    elif req.status_code != 200:
        raise LabAPIError(f"An unexpected error occurred while fetching lab data: {req.text}")
    else:
        lab_data = req.json()

    # Ugly way to retrieve name, but it doesn't use another network request
    name = list(lab_data["hours"].keys())[0]
    status = lab_data["hours"][name]["closed"]
    total_computers = len(lab_data["state"])
    off_computers = 0
    in_use_computers = 0
    available_computers = 0
    out_of_service_computers = 0

    # Computer States: Off, Available, In Use, Out of Service
    # Off: 0
    # Available: 1
    # In Use: 2
    # Out of Service: 3
    # https://github.com/pittcsc/PittAPI/issues/192#issuecomment-2323735463
    for computer_info in lab_data["state"].values():
        up = computer_info["up"]
        if up == 0:
            off_computers += 1
        elif up == 1:
            available_computers += 1
        elif up == 2:
            in_use_computers += 1
        elif up == 3:
            out_of_service_computers += 1
        else:
            raise LabAPIError(f"Unknown 'up' value for {computer_info["addr"]} in {name}: {up}")

    return Lab(
        name,
        status,
        available_computers,
        off_computers,
        in_use_computers,
        out_of_service_computers,
        total_computers,
    )


def get_all_labs_data() -> list[Lab]:
    """Returns a list with status and amount of OS machines for all labs.

    Returns:
        list[Lab]: A list of Labs.
    """

    all_lab_data = [get_one_lab_data(lab_name) for lab_name in AVAIL_LAB_ID_MAP.keys()]

    return all_lab_data

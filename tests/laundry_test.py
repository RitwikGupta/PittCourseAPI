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

import unittest
import responses
import json

from pathlib import Path

from pittapi import laundry
from pittapi.laundry import BuildingStatus

SAMPLE_PATH = Path() / "tests" / "samples"


class LaundryTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with open(SAMPLE_PATH / "laundry_mock_response_holland.json", "r") as file:
            self.mock_data_holland = json.load(file)
        with open(SAMPLE_PATH / "laundry_mock_response_towers.json", "r") as file:
            self.mock_data_towers = json.load(file)

    @responses.activate
    def test_get_building_status_holland(self):
        test_building = "HOLLAND"
        responses.add(
            responses.GET,
            laundry.BASE_URL.format(location=laundry.LOCATION_LOOKUP[test_building]),
            json=self.mock_data_holland,
            status=200,
        )
        status = laundry.get_building_status(test_building)
        self.assertEqual(
            status,
            BuildingStatus(building=test_building, free_washers=0, free_dryers=15, total_washers=14, total_dryers=21),
        )

    @responses.activate
    def test_get_laundry_machine_statuses_holland(self):
        test_building = "HOLLAND"
        responses.add(
            responses.GET,
            laundry.BASE_URL.format(location=laundry.LOCATION_LOOKUP[test_building]),
            json=self.mock_data_holland,
            status=200,
        )
        machines = laundry.get_laundry_machine_statuses(test_building)
        self.assertEqual(len(machines), 35)
        for machine in machines:
            if machine.status in ("Available", "Idle", "Ext. Cycle") or "remaining" in machine.status:
                self.assertIsNotNone(machine.time_left)
            elif machine.status in ("Out of service", "Offline"):
                self.assertIsNone(machine.time_left)
            else:
                self.fail(f"Invalid machine status detected for {machine=}")

    @responses.activate
    def test_get_building_status_towers(self):
        test_building = "TOWERS"
        responses.add(
            responses.GET,
            laundry.BASE_URL.format(location=laundry.LOCATION_LOOKUP[test_building]),
            json=self.mock_data_towers,
            status=200,
        )
        status = laundry.get_building_status(test_building)
        self.assertEqual(
            status,
            BuildingStatus(building=test_building, free_washers=1, free_dryers=1, total_washers=54, total_dryers=55),
        )

    @responses.activate
    def test_get_laundry_machine_statuses_towers(self):
        test_building = "TOWERS"
        responses.add(
            responses.GET,
            laundry.BASE_URL.format(location=laundry.LOCATION_LOOKUP[test_building]),
            json=self.mock_data_towers,
            status=200,
        )
        machines = laundry.get_laundry_machine_statuses(test_building)
        self.assertEqual(len(machines), 109)
        for machine in machines:
            if machine.status in ("Available", "Idle", "Ext. Cycle") or "remaining" in machine.status:
                self.assertIsNotNone(machine.time_left)
            elif machine.status in ("Out of service", "Offline"):
                self.assertIsNone(machine.time_left)
            else:
                self.fail(f"Invalid machine status detected for {machine=}")

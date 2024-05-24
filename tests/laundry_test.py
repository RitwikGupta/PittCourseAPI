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

SAMPLE_PATH = Path() / "tests" / "samples"
TEST_BUILDING = "SUTH_EAST"


class LaundryTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with open(SAMPLE_PATH / "laundry_mock_response.json", "r") as file:
            self.mock_data = json.load(file)

    @responses.activate
    def test_get_status_simple(self):
        responses.add(
            responses.GET,
            "https://www.laundryview.com/api/currentRoomData?school_desc_key=197&location="
            + laundry.LOCATION_LOOKUP[TEST_BUILDING],
            json=self.mock_data,
            status=200,
        )
        status = laundry.get_status_simple(TEST_BUILDING)
        self.assertIsInstance(status, dict)
        self.assertEqual(status["building"], TEST_BUILDING)
        self.assertEqual(status["free_washers"], 7)
        self.assertEqual(status["free_dryers"], 2)
        self.assertEqual(status["total_washers"], 10)
        self.assertEqual(status["total_dryers"], 10)

    @responses.activate
    def test_get_status_detailed(self):
        responses.add(
            responses.GET,
            "https://www.laundryview.com/api/currentRoomData?school_desc_key=197&location="
            + laundry.LOCATION_LOOKUP[TEST_BUILDING],
            json=self.mock_data,
            status=200,
        )
        status = laundry.get_status_detailed(TEST_BUILDING)
        self.assertIsInstance(status, list)

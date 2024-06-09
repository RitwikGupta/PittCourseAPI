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

import json
import unittest
import responses
import datetime

from pathlib import Path

from pittapi import dining

SAMPLE_PATH = Path() / "tests" / "samples"


class DiningTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (SAMPLE_PATH / "dining_schedule.json").open() as f:
            self.dining_schedule_data = json.load(f)

        with (SAMPLE_PATH / "dining_locations.json").open() as f:
            self.dining_locations_data = json.load(f)

        with (SAMPLE_PATH / "dining_menu.json").open() as f:
            self.dining_menu_data = json.load(f)

    @responses.activate
    def test_get_locations(self):
        responses.add(
            responses.GET,
            "https://api.dineoncampus.com/v1/locations/status?site_id=5e6fcc641ca48e0cacd93b04&platform=",
            json=self.dining_locations_data,
            status=200,
        )
        self.assertIsInstance(dining.get_locations(), dict)

    @responses.activate
    def test_get_location_hours(self):
        responses.add(
            responses.GET,
            "https://api.dineoncampus.com/v1/locations/weekly_schedule?site_id=5e6fcc641ca48e0cacd93b04&date=%222024-04-12%22",
            json=self.dining_schedule_data,
            status=200,
        )

        self.assertIsInstance(
            dining.get_location_hours("The Eatery", datetime.datetime(2024, 4, 12)),
            dict,
        )

    @responses.activate
    def test_get_location_menu(self):
        responses.add(
            responses.GET,
            "https://api.dineoncampus.com/v1/locations/status?site_id=5e6fcc641ca48e0cacd93b04&platform=",
            json=self.dining_locations_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.dineoncampus.com/v1/location/610b1f78e82971147c9f8ba5/periods?platform=0&date=24-04-12",
            json=self.dining_menu_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.dineoncampus.com/v1/location/610b1f78e82971147c9f8ba5/periods/659daa4d351d53068df67835?platform=0&date=24-04-12",
            json=self.dining_menu_data,
            status=200,
        )
<<<<<<< HEAD
        locations = dining.get_location_menu(
            "The Eatery", datetime.datetime(2024, 4, 12), "Breakfast"
        )
=======
        locations = dining.get_location_menu("The Eatery", datetime.datetime(2024, 4, 12), "Breakfast")
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6
        self.assertIsInstance(locations, dict)

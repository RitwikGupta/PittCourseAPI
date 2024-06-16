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

from pittapi import shuttle


class ShuttleTest(unittest.TestCase):
    @responses.activate
    def test_get_map_vehicle_points(self):
        responses.add(
            method=responses.GET,
            url=f"{shuttle.VEHICLE_POINTS_URL}?ApiKey={shuttle.API_KEY}",
            json=[{}, {}, {}],
            status=200,
        )
        self.assertIsInstance(shuttle.get_map_vehicle_points(), list)

    @responses.activate
    def test_get_route_stop_arrivals(self):
        responses.add(
            method=responses.GET,
            url=f"{shuttle.STOP_ESTIMATES_URL}?ApiKey={shuttle.API_KEY}&TimesPerStopString=1",
            json=[{}, {}, {}],
            status=200,
        )
        self.assertIsInstance(shuttle.get_route_stop_arrivals(), list)

    @responses.activate
    def test_vehicle_route_stop_estimates(self):
        responses.add(
            method=responses.GET,
            url=f"{shuttle.STOP_ESTIMATES_URL}?vehicleIdStrings=25&quantity=4",
            json=[{"Estimates": [{}, {}, {}, {}]}],
            status=200,
        )
        stop_estimates = shuttle.get_vehicle_route_stop_estimates("25", 4)
        self.assertIsInstance(stop_estimates, list)
        self.assertEqual(len(stop_estimates[0]["Estimates"]), 4)

    @responses.activate
    def test_get_routes(self):
        responses.add(
            method=responses.GET,
            url=f"{shuttle.ROUTES_URL}?ApiKey={shuttle.API_KEY}",
            json=[{}, {}, {}],
            status=200,
        )
        self.assertIsInstance(shuttle.get_routes(), list)

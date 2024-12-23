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

from pathlib import Path

from pittapi import people


SAMPLE_PATH = Path() / "tests" / "samples"


class PeopleTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with open(SAMPLE_PATH / "people_ramirez_mock_response.html") as f:
            self.ramirez_test_data = f.read()
        with open(SAMPLE_PATH / "people_too_many_mock_response.html") as f:
            self.too_many_test_data = f.read()
        with open(SAMPLE_PATH / "people_none_mock_response.html") as f:
            self.none_found_test_data = f.read()

    @responses.activate
    def test_people_get_person(self):
        responses.add(
            responses.POST,
            people.PEOPLE_SEARCH_URL,
            body=self.ramirez_test_data,
            status=200,
        )
        ans = people.get_person("John C Ramirez")
        self.assertIsInstance(ans, list)
        self.assertTrue(ans[0]["name"] == "Ramirez, John C")
        self.assertTrue(ans[0]["office_phone"] == "(412) 624-8441")

    @responses.activate
    def test_people_get_person_too_many(self):
        responses.add(
            responses.POST,
            people.PEOPLE_SEARCH_URL,
            body=self.too_many_test_data,
            status=200,
        )
        ans = people.get_person("Smith")
        self.assertIsInstance(ans, list)
        self.assertEqual(ans, [{"ERROR": "Too many people matched your criteria."}])

    @responses.activate
    def test_people_get_person_none(self):
        responses.add(
            responses.POST,
            people.PEOPLE_SEARCH_URL,
            body=self.none_found_test_data,
            status=200,
        )
        ans = people.get_person("Lebron Iverson James Jordan Kobe")
        self.assertIsInstance(ans, list)
        self.assertEqual(ans, [{"ERROR": "No one found."}])

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
from pathlib import Path

import responses

from pittapi import library

SAMPLE_PATH = Path() / "tests" / "samples"

# Put path to Hillman Library Study Rooms mock response and run unit test
HILLMAN_STUDY_ROOMS_PATH = None


class LibraryTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (SAMPLE_PATH / "library_mock_response_water.json").open() as f:
            self.library_query = json.load(f)

    @responses.activate
    def test_get_documents(self):
        responses.add(
            responses.GET,
            library.LIBRARY_URL + library.QUERY_START + "water",
            json=self.library_query,
            status=200,
        )
        query_result = library.get_documents("water")
        self.assertIsInstance(query_result, dict)
        self.assertEqual(query_result["pages"], 10)
        self.assertEqual(len(query_result["docs"]), 10)
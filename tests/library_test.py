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

SAMPLE_PATH = Path(__file__).parent / "samples"


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


class StudyRoomTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (SAMPLE_PATH / "hillman_study_room_mock_response.json").open() as f:
            self.hillman_query = json.load(f)

    @responses.activate
    def test_hillman_total_reserved(self):
        responses.add(
            responses.GET,
            library.STUDY_ROOMS_URL,
            json=self.hillman_query,
            status=200,
        )
        self.assertEqual(
            library.hillman_total_reserved(), {"Total Hillman Reservations": 4}
        )

    @responses.activate
    def test_reserved_hillman_times(self):
        responses.add(
            responses.GET,
            library.STUDY_ROOMS_URL,
            json=self.hillman_query,
            status=200,
        )
        mock_answer = [
            {
                "Room": "408 HL (Max. 5 persons) (Enclosed Room)",
                "Reserved": ["2024-06-12 17:30:00", "2024-06-12 20:30:00"],
            },
            {
                "Room": "409 HL (Max. 5 persons) (Enclosed Room)",
                "Reserved": ["2024-06-12 18:00:00", "2024-06-12 21:00:00"],
            },
            {
                "Room": "303 HL (Max. 5 persons) (Enclosed Room)",
                "Reserved": ["2024-06-12 18:30:00", "2024-06-12 21:30:00"],
            },
            {
                "Room": "217 HL (Max. 10 persons) (Enclosed Room)",
                "Reserved": ["2024-06-12 19:00:00", "2024-06-12 22:30:00"],
            },
        ]
        self.assertEqual(mock_answer, library.reserved_hillman_times())

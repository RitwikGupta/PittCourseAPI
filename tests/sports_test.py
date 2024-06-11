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
from unittest.mock import MagicMock

from pittapi import sports


class LibraryTest(unittest.TestCase):
    def setUp(self):
        mocked_basketball_data = {
            "team": {
                "id": "221",
                "record": {
                    "items": [
                        {
                            "description": "Overall Record",
                            "type": "total",
                            "summary": "11-21",
                        },
                        {
                            "description": "Home Record",
                            "type": "home",
                            "summary": "9-11",
                        },
                    ]
                },
                "nextEvent": [
                    {
                        "date": "2022-03-08T19:00Z",
                        "competitions": [
                            {
                                "venue": {
                                    "fullName": "Barclays Center",
                                    "address": {"city": "Brooklyn", "state": "NY"},
                                },
                                "competitors": [
                                    {
                                        "id": "221",
                                        "homeAway": "home",
                                        "team": {
                                            "id": "221",
                                            "location": "Pittsburgh",
                                            "nickname": "Pittsburgh",
                                            "abbreviation": "PITT",
                                            "displayName": "Pittsburgh Panthers",
                                        },
                                    },
                                    {
                                        "id": "103",
                                        "homeAway": "away",
                                        "team": {
                                            "id": "103",
                                            "location": "Boston College",
                                            "nickname": "Boston College",
                                            "abbreviation": "BC",
                                            "displayName": "Boston College Eagles",
                                        },
                                    },
                                ],
                                "status": {"type": {"name": "STATUS_FINAL"}},
                            }
                        ],
                    }
                ],
                "standingSummary": "12th in ACC",
            }
        }
        mocked_football_data = {
            "team": {
                "id": "221",
                "name": "Pittsburgh",
                "record": {
                    "items": [
                        {
                            "description": "Overall Record",
                            "type": "total",
                            "summary": "10-2",
                        },
                        {
                            "description": "Home Record",
                            "type": "home",
                            "summary": "5-2",
                        },
                    ]
                },
                "nextEvent": [
                    {
                        "id": "401405793",
                        "date": "2022-03-08T19:00Z",
                        "name": "Pittsburgh Panthers at Wake Forest Deamon Deacons",
                        "competitions": [
                            {
                                "venue": {
                                    "fullName": "Bank of America Stadium",
                                    "address": {"city": "Charlotte", "state": "NC"},
                                },
                                "competitors": [
                                    {
                                        "id": "221",
                                        "homeAway": "away",
                                        "team": {
                                            "id": "221",
                                            "location": "Pittsburgh",
                                            "nickname": "Pittsburgh",
                                            "abbreviation": "PITT",
                                            "displayName": "Pittsburgh Panthers",
                                        },
                                    },
                                    {
                                        "id": "104",
                                        "homeAway": "away",
                                        "team": {
                                            "id": "103",
                                            "location": "Wake Forest",
                                            "nickname": "Wake Forest",
                                            "abbreviation": "WAKE",
                                            "displayName": "Wake Forest Deamon Deacons",
                                        },
                                    },
                                ],
                                "status": {"type": {"name": "STATUS_IN_PROGRESS"}},
                            }
                        ],
                    }
                ],
                "standingSummary": "1st in ACC - Coastal",
            }
        }
        sports._get_mens_basketball_data = MagicMock(return_value=mocked_basketball_data)
        sports._get_football_data = MagicMock(return_value=mocked_football_data)

    def test_get_mens_basketball_record(self):
        self.assertEqual("11-21", sports.get_mens_basketball_record())

    def test_get_mens_basketball_record_offseason(self):
        offseason_data = {"team": {"id": "221", "record": {}}}
        sports._get_mens_basketball_data = MagicMock(return_value=offseason_data)

        self.assertEqual("There's no record right now.", sports.get_mens_basketball_record())

    def test_get_football_record(self):
        self.assertEqual("10-2", sports.get_football_record())

    def test_get_football_record_offseason(self):
        offseason_data = {"team": {"id": "221", "record": {}}}
        sports._get_football_data = MagicMock(return_value=offseason_data)

        self.assertEqual("There's no record right now.", sports.get_football_record())

    def test_get_mens_basketball_standings(self):
        self.assertEqual("12th in ACC", sports.get_mens_basketball_standings())

    def test_get_football_standings(self):
        self.assertEqual("1st in ACC - Coastal", sports.get_football_standings())

    def test_get_next_mens_basketball_game(self):
        next_game_details = sports.get_next_mens_basketball_game()
        self.assertIn("timestamp", next_game_details)
        self.assertIn("opponent", next_game_details)
        self.assertIn("home_away", next_game_details)
        self.assertIn("location", next_game_details)
        self.assertIn("status", next_game_details)
        self.assertNotEqual("NO_GAME_SCHEDULED", next_game_details["status"])

    def test_get_next_football_game(self):
        next_game_details = sports.get_next_football_game()
        self.assertIn("timestamp", next_game_details)
        self.assertIn("opponent", next_game_details)
        self.assertIn("home_away", next_game_details)
        self.assertIn("location", next_game_details)
        self.assertIn("status", next_game_details)
        self.assertNotEqual("NO_GAME_SCHEDULED", next_game_details["status"])

    def test_get_next_mens_basketball_game_offseason(self):
        offseason_data = {"team": {"nextEvent": []}}
        sports._get_mens_basketball_data = MagicMock(return_value=offseason_data)

        next_game_details = sports.get_next_mens_basketball_game()
        self.assertEqual(1, len(next_game_details))
        self.assertIn("status", next_game_details)
        self.assertEqual("NO_GAME_SCHEDULED", next_game_details["status"])

    def test_get_next_football_game_offseason(self):
        offseason_data = {"team": {"nextEvent": []}}
        sports._get_football_data = MagicMock(return_value=offseason_data)

        next_game_details = sports.get_next_football_game()
        self.assertEqual(1, len(next_game_details))
        self.assertIn("status", next_game_details)
        self.assertEqual("NO_GAME_SCHEDULED", next_game_details["status"])

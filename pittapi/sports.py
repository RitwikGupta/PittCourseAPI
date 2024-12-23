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

import requests

FOOTBALL_URL = (
    "http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/pitt"
)
MENS_BASKETBALL_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/pittsburgh"


def get_mens_basketball_record() -> str:
    """returns the current record of the men's basketball team"""
    basketball_data = _get_mens_basketball_data()

    try:
        record_summary = basketball_data["team"]["record"]["items"][0]["summary"]

    except KeyError:
        record_summary = "There's no record right now."

    return record_summary


def get_next_mens_basketball_game() -> dict:
    """returns a dict containing details of the next scheduled men's basketball game."""
    basketball_data = _get_mens_basketball_data()
    next_game = None
    try:
        next_game = basketball_data["team"]["nextEvent"][0]
        opponent = None
        homeaway = None
        status = None
        if next_game["competitions"][0]["status"]["type"]["name"] == "STATUS_FINAL":
            status = "GAME_COMPLETE"
        elif (
            next_game["competitions"][0]["status"]["type"]["name"]
            == "STATUS_IN_PROGRESS"
        ):
            status = "IN_PROGRESS"
        if next_game["competitions"][0]["competitors"][0]["id"] == 221:
            opponent = next_game["competitions"][0]["competitors"][0]
            homeaway = next_game["competitions"][0]["competitors"][0]["homeAway"]
        else:
            opponent = next_game["competitions"][0]["competitors"][1]
            homeaway = next_game["competitions"][0]["competitors"][1]["homeAway"]
        return {
            "timestamp": next_game["date"],
            "opponent": {
                "id": opponent["team"]["id"],
                "school": opponent["team"]["nickname"],
                "name": opponent["team"]["displayName"],
            },
            "home_away": homeaway,
            "location": {
                "full_name": next_game["competitions"][0]["venue"]["fullName"],
                "address": next_game["competitions"][0]["venue"]["address"],
            },
            "status": status,
        }
    except IndexError:
        # IndexError occurs when a next game on the schedule is not present
        return {"status": "NO_GAME_SCHEDULED"}


def get_mens_basketball_standings() -> str:
    """returns a string describing the placement of the men's basketball team. eg: '14th in ACC'"""
    basketball_data = _get_mens_basketball_data()

    return_value = basketball_data["team"]["standingSummary"]
    return return_value


def get_football_record() -> str:
    """returns the current record of the men's football team"""
    football_data = _get_football_data()

    try:
        record_summary = football_data["team"]["record"]["items"][0]["summary"]

    except KeyError:
        record_summary = "There's no record right now."

    return record_summary


def get_next_football_game() -> dict:
    football_data = _get_football_data()
    next_game = None
    try:
        next_game = football_data["team"]["nextEvent"][0]
        opponent = None
        homeaway = None
        status = None
        if next_game["competitions"][0]["status"]["type"]["name"] == "STATUS_FINAL":
            status = "GAME_COMPLETE"
        elif (
            next_game["competitions"][0]["status"]["type"]["name"]
            == "STATUS_IN_PROGRESS"
        ):
            status = "IN_PROGRESS"
        if next_game["competitions"][0]["competitors"][0]["id"] == 221:
            opponent = next_game["competitions"][0]["competitors"][1]
            homeaway = next_game["competitions"][0]["competitors"][0]["homeAway"]
        else:
            opponent = next_game["competitions"][0]["competitors"][0]
            homeaway = next_game["competitions"][0]["competitors"][1]["homeAway"]
        return {
            "timestamp": next_game["date"],
            "opponent": {
                "id": opponent["team"]["id"],
                "school": opponent["team"]["nickname"],
                "name": opponent["team"]["displayName"],
            },
            "home_away": homeaway,
            "location": {
                "full_name": next_game["competitions"][0]["venue"]["fullName"],
                "address": next_game["competitions"][0]["venue"]["address"],
            },
            "status": status,
        }
    except IndexError:
        # IndexError occurs when a next game on the schedule is not present
        return {"status": "NO_GAME_SCHEDULED"}


def get_football_standings() -> str:
    """returns a string describing the placement of the football team. eg: '14th in ACC'"""
    football_data = _get_football_data()

    return_value = football_data["team"]["standingSummary"]
    return return_value


def _get_mens_basketball_data() -> dict:
    return requests.get(MENS_BASKETBALL_URL).json()


def _get_football_data() -> dict:
    return requests.get(FOOTBALL_URL).json()

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
from typing import Any


def get_status() -> dict[str, list[Any]]:
    """Gets status information about all Pitt services"""
    status = requests.get("https://status.pitt.edu/index.json")
    data = status.json()
    components = [
        {
            "status": component["status"],
            "name": component["name"],
            "updated_at": component["updated_at"],
            "description": component["description"],
        }
        for component in data["components"]
    ]
    incidents = [
        {
            "components": [
                {
                    "status": component["status"],
                    "name": component["name"],
                    "updated_at": component["updated_at"],
                    "description": component["description"],
                }
                for component in incident["components"]
            ],
            "incident_updates": [
                {
                    "affected_components": [
                        {
                            "name": component["name"],
                            "new_status": component["new_status"],
                            "old_status": component["old_status"],
                        }
                        for component in update["affected_components"]
                    ],
                    "body": update["body"],
                    "status": update["status"],
                    "updated_at": update["updated_at"],
                }
                for update in incident["incident_updates"]
            ],
            "impact": incident["impact"],
            "name": incident["name"],
            "status": incident["status"],
            "resolved_at": incident["resolved_at"],
            "updated_at": incident["updated_at"],
        }
        for incident in data["incidents"]
    ]
    ret = {"components": components, "incidents": incidents}

    return ret

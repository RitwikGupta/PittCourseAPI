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


JSON = dict[str, Any]

API_KEY = "8882812681"
VEHICLE_POINTS_URL = (
    "http://www.pittshuttle.com/Services/JSONPRelay.svc/GetMapVehiclePoints"
)
ARRIVAL_TIMES_URL = (
    "http://www.pittshuttle.com/Services/JSONPRelay.svc/GetRouteStopArrivals"
)
STOP_ESTIMATES_URL = (
    "http://www.pittshuttle.com/Services/JSONPRelay.svc/GetVehicleRouteStopEstimates"
)
ROUTES_URL = "http://www.pittshuttle.com/Services/JSONPRelay.svc/GetRoutesForMap"

sess = requests.session()


def get_map_vehicle_points(api_key: str = API_KEY) -> JSON:
    """Return the map location for all active vehicles."""
    payload = {"ApiKey": api_key}
    response = sess.get(VEHICLE_POINTS_URL, params=payload)
    response_json: JSON = response.json()
    return response_json


def get_route_stop_arrivals(api_key: str = API_KEY, times_per_stop: int = 1) -> JSON:
    """Return stop arrival times for all vehicles."""
    payload = {"ApiKey": api_key, "TimesPerStopString": str(times_per_stop)}
    response = sess.get(ARRIVAL_TIMES_URL, params=payload)
    response_json: JSON = response.json()
    return response_json


def get_vehicle_route_stop_estimates(vehicle_id: str, quantity: int = 2) -> JSON:
    """Return {quantity} stop estimates for all active vehicles."""
    payload = {"vehicleIdStrings": vehicle_id, "quantity": str(quantity)}
    response = sess.get(STOP_ESTIMATES_URL, params=payload)
    response_json: JSON = response.json()
    return response_json


def get_routes(api_key: str = API_KEY) -> JSON:
    """Return the routes with Vehicle Route Name, Vehicle ID, and all stops, etc."""
    payload = {"ApiKey": api_key}
    response = sess.get(ROUTES_URL, params=payload)
    response_json: JSON = response.json()
    return response_json

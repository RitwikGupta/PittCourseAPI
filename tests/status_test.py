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

from pathlib import Path

from pittapi import status

SAMPLE_PATH = Path() / "tests" / "samples"


class StatusTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (SAMPLE_PATH / "status.json").open() as f:
            self.status_data = json.load(f)

    @responses.activate
    def test_get_status(self):
        responses.add(responses.GET, "https://status.pitt.edu/index.json", json=self.status_data, status=200)
        self.assertIsInstance(status.get_status(), dict)

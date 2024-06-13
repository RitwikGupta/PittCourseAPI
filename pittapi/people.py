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

from requests_html import HTMLSession

# Please note that find.pitt.edu will not accept more than 10 requests within a few minutes
# It will time out if that happens

PEOPLE_SEARCH_URL = "https://find.pitt.edu/Search"

LABEL_CONVERSION = {
    "Email": "email",
    "Nickname": "nickname",
    "Student Campus": "campus",
    "Student Plan(s)": "academic_plan",
    "Web Page": "website",
    "Employee Information": "employment_info",
    "Office Phone": "office_phone",
    "Office Mailing Address": "office_mailing_address",
    "Office Location Address": "office_location_address",
    "Mobile Phone": "mobile_phone",
    "UPMC Department": "upmc_department",
    "UPMC Position": "upmc_position",
    "UPMC Email": "upmc_email",
}


def _parse_segments(person: dict, segments: list[str]) -> None:
    label = None
    for segment in segments:
        if "class" in segment.attrs and "row-label" in segment.attrs["class"]:
            if segment.text in LABEL_CONVERSION:
                label = LABEL_CONVERSION[segment.text]
            elif segment.text == "":
                continue
            else:
                label = None
        elif label:
            if label in person:
                if not isinstance(person[label], list):
                    person[label] = [person[label]]
                person[label].append(segment.text)
            else:
                person[label] = segment.text


def get_person(query: str) -> list[dict[str, str]]:
    payload = {"search": query}
    session = HTMLSession()
    resp = session.post(PEOPLE_SEARCH_URL, data=payload)
    if resp.text.__contains__("Too many people matched your criteria."):
        return [{"ERROR": "Too many people matched your criteria."}]  # Return an error
    elements = resp.html.xpath("/html/div/section")
    result = []
    for entry in elements:
        name, *segments = entry.find("span")
        person = {"name": name.text}
        _parse_segments(person, segments)
        result.append(person)
    if result == []:
        return [{"ERROR": "No one found."}]  # Return an error
    return result

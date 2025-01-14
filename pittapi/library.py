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

from __future__ import annotations

import requests
from typing import Any, NamedTuple

LIBRARY_URL = (
    "https://pitt.primo.exlibrisgroup.com/primaws/rest/pub/pnxs"
    "?acTriggered=false&blendFacetsSeparately=false&citationTrailFilterByAvailability=true&disableCache=false&getMore=0"
    "&inst=01PITT_INST&isCDSearch=false&lang=en&limit=10&newspapersActive=false&newspapersSearch=false&offset=0"
    "&otbRanking=false&pcAvailability=false&qExclude=&qInclude=&rapido=false&refEntryActive=false&rtaLinks=true"
    "&scope=MyInst_and_CI&searchInFulltextUserSelection=false&skipDelivery=Y&sort=rank&tab=Everything"
    "&vid=01PITT_INST:01PITT_INST"
)
STUDY_ROOMS_URL = (
    "https://pitt.libcal.com/spaces/bookings/search"
    "?lid=917&gid=1558&eid=0&seat=0&d=1&customDate=&q=&daily=0&draw=1&order%5B0%5D%5Bcolumn%5D=1&order%5B0%5D%5Bdir%5D=asc"
    "&start=0&length=25&search%5Bvalue%5D=&_=1717907260661"
)

QUERY_START = "&q=any,contains,"

sess = requests.session()


class Document(NamedTuple):
    # Field names must exactly match key names in JSON data
    title: list[str] | None = None
    language: list[str] | None = None
    subject: list[str] | None = None
    format: list[str] | None = None
    type: list[str] | None = None
    isbns: list[str] | None = None
    description: list[str] | None = None
    publisher: list[str] | None = None
    edition: list[str] | None = None
    genre: list[str] | None = None
    place: list[str] | None = None
    creator: list[str] | None = None
    version: list[str] | None = None
    creationdate: list[str] | None = None


class QueryResult(NamedTuple):
    num_results: int
    num_pages: int
    docs: list[Document]


class Reservation(NamedTuple):
    room: str
    reserved_from: str
    reserved_until: str


def get_documents(query: str) -> QueryResult:
    """Return ten resource results from the specified page"""
    parsed_query = query.replace(" ", "+")
    full_query = LIBRARY_URL + QUERY_START + parsed_query
    resp = sess.get(full_query)
    resp_json = resp.json()

    results = QueryResult(
        num_results=resp_json["info"]["total"],
        num_pages=resp_json["info"]["last"],
        docs=_filter_documents(resp_json["docs"]),
    )
    return results


def get_document_by_bookmark(bookmark: str) -> QueryResult:
    """Return resource referenced by bookmark"""
    payload = {"bookMark": bookmark}
    resp = sess.get(LIBRARY_URL, params=payload)
    resp_json = resp.json()

    if resp_json.get("errors"):
        for error in resp_json.get("errors"):
            if error["code"] == "invalid.bookmark.format":
                raise ValueError("Invalid bookmark")
    results = QueryResult(
        num_results=resp_json["info"]["total"],
        num_pages=resp_json["info"]["last"],
        docs=_filter_documents(resp_json["docs"]),
    )
    return results


def _filter_documents(documents: list[dict[str, Any]]) -> list[Document]:
    new_docs: list[Document] = []

    for doc in documents:
        filtered_doc = {key: vals for key, vals in doc["pnx"]["display"].items() if key in Document._fields}
        new_docs.append(Document(**filtered_doc))

    return new_docs


def hillman_total_reserved() -> int:
    """Returns a simple count dictionary of the total amount of reserved rooms appointments"""
    resp = requests.get(STUDY_ROOMS_URL)
    resp_json = resp.json()
    total_records: int = resp_json["recordsTotal"]  # Total records is kept track of by default in the JSON

    # Note: this must align with the amount of entries in reserved times function; renamed for further clarification
    return total_records


def reserved_hillman_times() -> list[Reservation]:
    """Returns a list of dictionaries of reserved rooms in Hillman with their respective times"""
    resp = requests.get(STUDY_ROOMS_URL)
    resp_json = resp.json()
    data = resp_json["data"]

    if data is None:
        return []

    # Note: there can be multiple reservations in the same room, so we must use a list of maps and not a singular map
    bookings = [
        Reservation(
            room=reservation["itemName"],
            reserved_from=reservation["from"],
            reserved_until=reservation["to"],
        )
        for reservation in data
    ]
    return bookings

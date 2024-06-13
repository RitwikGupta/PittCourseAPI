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
from html.parser import HTMLParser
from typing import Any

LIBRARY_URL = (
    "https://pitt.primo.exlibrisgroup.com/primaws/rest/pub/pnxs"
    "?acTriggered=false&blendFacetsSeparately=false"
    "&citationTrailFilterByAvailability=true&disableCache=false&getMore=0"
    "&inst=01PITT_INST&isCDSearch=false&lang=en&limit=10&newspapersActive=false"
    "&newspapersSearch=false&offset=0&otbRanking=false&pcAvailability=false"
    "&qExclude=&qInclude=&rapido=false&refEntryActive=false&rtaLinks=true"
    "&scope=MyInst_and_CI&searchInFulltextUserSelection=false&skipDelivery=Y"
    "&sort=rank&tab=Everything&vid=01PITT_INST:01PITT_INST"
)

QUERY_START = "&q=any,contains,"

sess = requests.session()


class HTMLStrip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.data = []

    def handle_data(self, d: str) -> None:
        self.data.append(d)

    def get_data(self) -> str:
        return "".join(self.data)


def get_documents(query: str, page: int = 1) -> dict[str, Any]:
    """Return ten resource results from the specified page"""
    parsed_query = query.replace(" ", "+")
    full_query = LIBRARY_URL + QUERY_START + parsed_query
    resp = sess.get(full_query)
    resp_json = resp.json()

    results = _extract_results(resp_json)
    return results


def get_document_by_bookmark(bookmark: str) -> dict[str, Any]:
    """Return resource referenced by bookmark"""
    payload = {"bookMark": bookmark}
    resp = sess.get(LIBRARY_URL, params=payload)
    resp_json = resp.json()

    if resp_json.get("errors"):
        for error in resp_json.get("errors"):
            if error["code"] == "invalid.bookmark.format":
                raise ValueError("Invalid bookmark")
    results = _extract_results(resp_json)
    return results


def _strip_html(html: str) -> str:
    strip = HTMLStrip()
    strip.feed(html)
    return strip.get_data()


def _extract_results(json: dict[str, Any]) -> dict[str, Any]:
    results = {
        "total_results": json["info"]["total"],
        "pages": json["info"]["last"],
        "docs": _extract_documents(json["docs"]),
    }
    return results


def _extract_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    new_docs = []
    keep_keys = {
        "title",
        "language",
        "subject",
        "format",
        "type",
        "isbns",
        "description",
        "publisher",
        "edition",
        "genre",
        "place",
        "creator",
        "edition",
        "version",
        "creationdate",
    }

    for doc in documents:
        new_doc = {}
        for key in set(doc["pnx"]["display"].keys()) & keep_keys:
            new_doc[key] = doc["pnx"]["display"][key]
        new_docs.append(new_doc)

    return new_docs


def _extract_facets(facet_fields: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    facets: dict[str, list[dict[str, Any]]] = {}
    for facet in facet_fields:
        facets[facet["display_name"]] = []
        for count in facet["counts"]:
            facets[facet["display_name"]].append({"value": count["value"], "count": count["count"]})

    return facets

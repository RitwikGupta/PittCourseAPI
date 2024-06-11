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

import re
import math
import requests
import grequests
from typing import Dict, List, Any

sess = requests.session()


def _load_n_items(feed: str, max_news_items: int):
    payload = {
        "feed": feed,
        "id": "",
        "_object": "kgoui_Rcontent_I0_Rcontent_I0",
        "start": 0,
    }

    request_objs = []
    for i in range(int(math.ceil(max_news_items / 10))):
        payload["start"] = i * 10
        request_objs.append(grequests.get("https://m.pitt.edu/news/index.json", params=payload))

    responses = grequests.imap(request_objs)

    return responses


def get_news(feed: str = "main_news", max_news_items: int = 10) -> List[Dict[str, Any]]:
    # feed indicates the desired news feed
    # 'main_news'      - main news
    # 'cssd'           - student announcements, on my pitt
    # 'news_chronicle' - the Pitt Chronicle news
    # 'news_alerts'    - crime alerts

    news = []

    resps = _load_n_items(feed, max_news_items)
    resps = [r.json()["response"]["regions"][0]["contents"] for r in resps]

    for resp in resps:
        for data in resp:
            fields = data["fields"]
            if fields["type"] == "loadMore":
                continue

            # TODO: Look into why this gives a Type Error during the news alert test.
            try:
                title = fields["title"]
                url = "https://m.pitt.edu" + fields["url"]["formatted"]
                news.append({"title": title, "url": url})
            except TypeError:
                continue

    return news[:max_news_items]

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

from functools import cache
import math
from requests_html import Element, HTMLResponse, HTMLSession
from typing import NamedTuple

NUM_ARTICLES_PER_PAGE = 20

PITT_BASE_URL = "https://www.pitt.edu"
PITTWIRE_URL = PITT_BASE_URL + "/pittwire"
FEATURES_ARTICLES_URL = PITTWIRE_URL + "/news/features-articles"
NEWS_BY_CATEGORY_URL = PITTWIRE_URL + (
    "/news/{category}?field_topics_target_id={topic_id}&field_article_date_value={year}"
    "&title={query}&field_category_target_id=All&page={page_num}"
)

sess = HTMLSession()


class Article(NamedTuple):
    title: str
    description: str
    url: str
    tags: list[str]

    @classmethod
    def from_html(cls, article_html: Element) -> Article:
        article_heading: Element = article_html.find("h2.news-card-title a", first=True)
        article_subheading: Element = article_html.find("p", first=True)
        article_tags_list: list[Element] = article_html.find("ul.news-card-tags li")

        article_title = article_heading.text.strip()
        article_url = PITT_BASE_URL + article_heading.attrs["href"]
        article_description = article_subheading.text.strip()
        article_tags = [tag.text.strip() for tag in article_tags_list]

        return cls(title=article_title, description=article_description, url=article_url, tags=article_tags)


@cache
def _scrape_categories() -> dict[str, str]:
    response: HTMLResponse = sess.get(PITTWIRE_URL)
    category_menu: Element = response.html.find("div#block-views-block-category-menu-category-menu", first=True)
    category_list: list[Element] = category_menu.find("ul.hamburger-menu-list li")
    category_map: dict[str, str] = {}
    for category in category_list:
        category_link: Element = category.find("a", first=True)
        category_url_name = category_link.attrs["href"].split("/")[-1]
        category_map[category.text.strip()] = category_url_name
    if not category_map:
        raise RuntimeError("No categories found, please open a GitHub issue")
    return category_map


@cache
def _scrape_topics() -> dict[str, int]:
    response: HTMLResponse = sess.get(FEATURES_ARTICLES_URL)
    main_content: Element = response.html.xpath("/html/body/div/main/div/section", first=True)
    topic_fieldset: Element = main_content.find("fieldset.form-item-field-topics-target-id", first=True)
    topic_options: list[Element] = topic_fieldset.find("option")
    topic_map: dict[str, int] = {}
    for topic_option in topic_options:
        if (topic_id := topic_option.attrs["value"].strip()) == "All":  # Skip placeholder "Topics" option
            continue
        topic_name = topic_option.text.strip()
        topic_map[topic_name] = int(topic_id)
    if not topic_map:
        raise RuntimeError("No topics found, please open a GitHub issue")
    return topic_map


def _get_page_articles(topic: str, category: str, query: str, year: int | None, page_num: int) -> list[Article]:
    topic_id_map = _scrape_topics()
    category_url_name_map = _scrape_categories()
    year_str = str(year) if year else ""
    page_num_str = str(page_num) if page_num else ""

    response: HTMLResponse = sess.get(
        NEWS_BY_CATEGORY_URL.format(
            category=category_url_name_map[category],
            topic_id=topic_id_map[topic],
            year=year_str,
            query=query,
            page_num=page_num_str,
        )
    )
    main_content: Element = response.html.xpath("/html/body/div/main/div/section", first=True)
    news_cards: list[Element] = main_content.find("div.news-card")
    page_articles = [Article.from_html(news_card) for news_card in news_cards]
    return page_articles


@cache
def get_categories() -> list[str]:
    category_url_name_map = _scrape_categories()
    return list(category_url_name_map.keys())


@cache
def get_topics() -> list[str]:
    topic_id_map = _scrape_topics()
    return list(topic_id_map.keys())


def get_articles_by_topic(
    topic: str,
    category: str = "Features & Articles",
    query: str = "",
    year: int | None = None,
    max_num_results: int = NUM_ARTICLES_PER_PAGE,
) -> list[Article]:
    topic_id_map = _scrape_topics()
    if topic not in topic_id_map:
        raise ValueError(f"'{topic}' is not a valid topic, must be one of the following: {get_topics()}")

    category_url_name_map = _scrape_categories()
    if category not in category_url_name_map:
        raise ValueError(f"'{category}' is not a valid category, must be one of the following: {get_categories()}")

    num_pages = math.ceil(max_num_results / NUM_ARTICLES_PER_PAGE)

    # Get articles sequentially and synchronously (i.e., not using grequests) because the news pages must stay in order
    results: list[Article] = []
    for page_num in range(num_pages):  # Page numbers in url are 0-indexed
        page_articles = _get_page_articles(topic, category, query, year, page_num)
        num_articles_to_add = min(len(page_articles), max_num_results - len(results))
        results.extend(page_articles[:num_articles_to_add])
    return results

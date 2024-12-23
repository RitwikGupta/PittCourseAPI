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

import responses
import unittest

from pathlib import Path

from pittapi import news

SAMPLE_PATH = Path() / "tests" / "samples"


class NewsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (
            SAMPLE_PATH / "news_university_news_features_articles_page_0.html"
        ).open() as f:
            self.university_news_features_articles_page_0 = f.read()
        with (
            SAMPLE_PATH / "news_university_news_features_articles_page_1.html"
        ).open() as f:
            self.university_news_features_articles_page_1 = f.read()
        with (
            SAMPLE_PATH / "news_university_news_features_articles_fulbright.html"
        ).open() as f:
            self.university_news_features_articles_fulbright = f.read()
        with (
            SAMPLE_PATH / "news_university_news_features_articles_2020.html"
        ).open() as f:
            self.university_news_features_articles_2020 = f.read()

    @responses.activate
    def test_get_articles_by_topic(self):
        responses.add(
            responses.GET,
            "https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value=&title="
            "&field_category_target_id=All",
            body=self.university_news_features_articles_page_0,
        )

        university_news_articles = news.get_articles_by_topic("university-news")

        self.assertEqual(len(university_news_articles), news.NUM_ARTICLES_PER_PAGE)
        self.assertEqual(
            university_news_articles[0],
            news.Article(
                title="Questions for the ‘Connecting King’",
                description="Vernard Alexander, the new director of Pitt’s Homewood Community Engagement Center, "
                "sees himself as the ultimate connector.",
                url="https://www.pitt.edu/pittwire/pittmagazine/features-articles/vernard-alexander-community-engagement",
                tags=["University News", "Community Impact"],
            ),
        )
        self.assertEqual(
            university_news_articles[-1],
            news.Article(
                title="John Surma is Pitt’s 2024 spring commencement speaker",
                description="The University will also honor the Board of Trustees member and former U. S. Steel CEO "
                "with an honorary degree.",
                url="https://www.pitt.edu/pittwire/features-articles/2024-spring-commencement-speaker-john-surma",
                tags=["University News", "Commencement"],
            ),
        )

    @responses.activate
    def test_get_articles_by_topic_query(self):
        query = "fulbright"
        responses.add(
            responses.GET,
            "https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value="
            f"&title={query}&field_category_target_id=All",
            body=self.university_news_features_articles_fulbright,
        )

        university_news_articles = news.get_articles_by_topic(
            "university-news", query=query
        )

        self.assertEqual(len(university_news_articles), 3)
        self.assertEqual(
            university_news_articles[0],
            news.Article(
                title="Meet Pitt’s 2024 faculty Fulbright winners",
                description="The Fulbright U.S. Scholar Program offers faculty the opportunity "
                "to teach and conduct research abroad.",
                url="https://www.pitt.edu/pittwire/features-articles/faculty-fulbright-scholars-2024",
                tags=[
                    "University News",
                    "Innovation and Research",
                    "Global",
                    "Faculty",
                ],
            ),
        )
        self.assertEqual(
            university_news_articles[-1],
            news.Article(
                title="Pitt has been named a top producer of Fulbright U.S. students for 2022-23",
                description="Meet the nine Pitt scholars in this year’s cohort.",
                url="https://www.pitt.edu/pittwire/features-articles/pitt-fulbright-top-producing-institution-2022-2023",
                tags=[
                    "University News",
                    "Global",
                    "David C. Frederick Honors College",
                    "Kenneth P. Dietrich School of Arts and Sciences",
                    "School of Education",
                    "Swanson School of Engineering",
                ],
            ),
        )

    @responses.activate
    def test_get_articles_by_topic_year(self):
        year = 2020
        responses.add(
            responses.GET,
            f"https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value={year}"
            "&title=&field_category_target_id=All",
            body=self.university_news_features_articles_2020,
        )

        university_news_articles = news.get_articles_by_topic(
            "university-news", year=year
        )

        self.assertEqual(len(university_news_articles), 5)
        self.assertEqual(
            university_news_articles[0],
            news.Article(
                title="University of Pittsburgh Library System acquires archive of renowned playwright August Wilson",
                description="The late playwright and Pittsburgh native is best known for his unprecedented "
                "American Century Cycle—10 plays that convey the Black experience in each decade of the 20th century. "
                "All 10 of the plays",
                url="https://www.pitt.edu/pittwire/features-articles/university-pittsburgh-library-system-acquires-archive-"
                "renowned-playwright-august-wilson",
                tags=["University News", "Arts and Humanities"],
            ),
        )
        self.assertEqual(
            university_news_articles[-1],
            news.Article(
                title="Track and field Olympian reflects on time at Pitt and plans for new facilities",
                description="Alumnus Herb Douglas (EDUC ’48, ’50G), the oldest living African American Olympic medalist, "
                "says plans for new training spaces for athletes will bring recruiting and Pitt Athletics to new heights.",
                url="https://www.pitt.edu/pittwire/features-articles/track-and-field-olympian-reflects-time-pitt-"
                "plans-new-facilities",
                tags=["University News", "Athletics"],
            ),
        )

    @responses.activate
    def test_get_articles_by_topic_less_than_one_page(self):
        num_results = 5
        responses.add(
            responses.GET,
            "https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value=&title="
            "&field_category_target_id=All",
            body=self.university_news_features_articles_page_0,
        )

        university_news_articles = news.get_articles_by_topic(
            "university-news", max_num_results=num_results
        )

        self.assertEqual(len(university_news_articles), num_results)
        self.assertEqual(
            university_news_articles[0],
            news.Article(
                title="Questions for the ‘Connecting King’",
                description="Vernard Alexander, the new director of Pitt’s Homewood Community Engagement Center, "
                "sees himself as the ultimate connector.",
                url="https://www.pitt.edu/pittwire/pittmagazine/features-articles/vernard-alexander-community-engagement",
                tags=["University News", "Community Impact"],
            ),
        )
        self.assertEqual(
            university_news_articles[-1],
            news.Article(
                title="Panthers Forward can now help graduates find loan forgiveness and repayment options",
                description="Pitt’s innovative debt-relief program has partnered with Savi, "
                "which can help some borrowers save thousands.",
                url="https://www.pitt.edu/pittwire/features-articles/panthers-forward-savi-affordability",
                tags=["University News", "Students"],
            ),
        )

    @responses.activate
    def test_get_articles_by_topic_multiple_pages(self):
        num_results = news.NUM_ARTICLES_PER_PAGE + 5
        responses.add(
            responses.GET,
            "https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value=&title="
            "&field_category_target_id=All",
            body=self.university_news_features_articles_page_0,
        )
        responses.add(
            responses.GET,
            "https://www.pitt.edu/pittwire/news/features-articles?field_topics_target_id=432&field_article_date_value=&title="
            "&field_category_target_id=All&page=1",
            body=self.university_news_features_articles_page_1,
        )

        university_news_articles = news.get_articles_by_topic(
            "university-news", max_num_results=num_results
        )

        self.assertEqual(len(university_news_articles), num_results)
        self.assertEqual(
            university_news_articles[0],
            news.Article(
                title="Questions for the ‘Connecting King’",
                description="Vernard Alexander, the new director of Pitt’s Homewood Community Engagement Center, "
                "sees himself as the ultimate connector.",
                url="https://www.pitt.edu/pittwire/pittmagazine/features-articles/vernard-alexander-community-engagement",
                tags=["University News", "Community Impact"],
            ),
        )
        self.assertEqual(
            university_news_articles[-1],
            news.Article(
                title="Pitt has 2 new Goldwater Scholars",
                description="The prestigious scholarship is awarded to sophomores and juniors who plan to pursue "
                "research careers in the sciences and engineering fields. Meet our winners.",
                url="https://www.pitt.edu/pittwire/features-articles/goldwater-scholars-2024",
                tags=[
                    "University News",
                    "Technology & Science",
                    "David C. Frederick Honors College",
                    "Kenneth P. Dietrich School of Arts and Sciences",
                ],
            ),
        )

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

from pittapi import textbook

import responses
import json
import unittest

from pathlib import Path
from pytest import mark
from requests import ConnectionError
from typing import Any

SAMPLE_PATH = Path() / "tests" / "samples"
CSRF_TOKEN = "1MTtTVOcQCCXDjKNKTqkfiwp0lmLWz1RvFy2ed65XeyGO4on-8zWsQpEAt4cjiH0glx9CIyjhAOKpXhIqDK_vg"
CS_SUBJECT_ID = "22457"
MATH_SUBJECT_ID = "22528"
CS_0441_GARRISON_SECTION_ID = "4558031"
MATH_0430_PAN_SECTION_ID = "4631097"


class TextbookTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        with (SAMPLE_PATH / "textbook_base_page.html").open() as f:
            self.html_text = f.read()
        with (SAMPLE_PATH / "textbook_subjects.json").open() as f:
            self.subjects_data = json.load(f)
        with (SAMPLE_PATH / "textbook_courses_CS.json").open() as f:
            self.cs_data = json.load(f)
        with (SAMPLE_PATH / "textbook_courses_MATH.json").open() as f:
            self.math_data = json.load(f)
        with (SAMPLE_PATH / "textbook_textbooks_CS_0441_garrison.json").open() as f:
            self.cs_0441_textbook_data: list[dict[str, Any]] = json.load(f)
        with (SAMPLE_PATH / "textbook_textbooks_MATH_0430_pan.json").open() as f:
            self.math_0430_textbook_data: list[dict[str, Any]] = json.load(f)

    def setUp(self):
        textbook.request_headers = None
        textbook.subject_map = None
        responses.start()

    def tearDown(self):
        responses.stop()
        responses.reset()

    def mock_base_site_success(self):
        responses.add(
            responses.GET, "https://pitt.verbacompare.com/", body=self.html_text
        )

    def mock_base_site_failure(self):
        responses.add(responses.GET, "https://pitt.verbacompare.com/", status=400)

    def mock_subject_map_success(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/departments/?term={textbook.CURRENT_TERM_ID}",
            json=self.subjects_data,
        )

    def mock_subject_map_failure(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/departments/?term={textbook.CURRENT_TERM_ID}",
            status=400,
        )

    def mock_cs_courses_success(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/courses/?id={CS_SUBJECT_ID}&term_id={textbook.CURRENT_TERM_ID}",
            json=self.cs_data,
        )

    def mock_cs_courses_failure(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/courses/?id={CS_SUBJECT_ID}&term_id={textbook.CURRENT_TERM_ID}",
            status=400,
        )

    def mock_cs_0441_garrison_books_success(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/books?id={CS_0441_GARRISON_SECTION_ID}",
            json=self.cs_0441_textbook_data,
        )

    def mock_cs_0441_garrison_books_none(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/books?id={CS_0441_GARRISON_SECTION_ID}",
            json=[],
        )

    def mock_math_courses_success(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/courses/?id={MATH_SUBJECT_ID}&term_id={textbook.CURRENT_TERM_ID}",
            json=self.math_data,
        )

    def mock_math_courses_failure(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/courses/?id={MATH_SUBJECT_ID}&term_id={textbook.CURRENT_TERM_ID}",
            status=400,
        )

    def mock_math_0430_pan_books_success(self):
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/books?id={MATH_0430_PAN_SECTION_ID}",
            json=self.math_0430_textbook_data,
        )

    def test_course_info(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num, instructor, section_num = (
            "CS",
            "0441",
            "GARRISON III",
            "1245",
        )

        course = textbook.CourseInfo(subject, course_num, instructor, section_num)

        self.assertEqual(course.subject, subject)
        self.assertEqual(course.course_num, course_num)
        self.assertEqual(course.instructor, instructor)
        self.assertEqual(course.section_num, section_num)

    def test_course_info_convert_input(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num, instructor, section_num = (
            "cs",
            "441",
            "garrison iii",
            "1245",
        )

        course = textbook.CourseInfo(subject, course_num, instructor, section_num)

        self.assertEqual(course.subject, "CS")
        self.assertEqual(course.course_num, "0441")
        self.assertEqual(course.instructor, "GARRISON III")
        self.assertEqual(course.section_num, section_num)

    def test_course_info_missing_instructor_and_section_num(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num = "cs", "0441"

        course = textbook.CourseInfo(subject, course_num)

        self.assertEqual(course.subject, "CS")
        self.assertEqual(course.course_num, "0441")
        self.assertIsNone(course.instructor)
        self.assertIsNone(course.section_num)

    def test_course_info_invalid_subject(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num, instructor, section_num = (
            "fake_subject",
            "0441",
            "GARRISON III",
            "1245",
        )

        self.assertRaises(
            LookupError,
            textbook.CourseInfo,
            subject,
            course_num,
            instructor,
            section_num,
        )

    def test_course_info_invalid_course_num(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num, instructor, section_num = (
            "cs",
            "abc",
            "GARRISON III",
            "1245",
        )

        self.assertRaises(
            ValueError,
            textbook.CourseInfo,
            subject,
            course_num,
            instructor,
            section_num,
        )

        course_num = "44111"

        self.assertRaises(
            ValueError,
            textbook.CourseInfo,
            subject,
            course_num,
            instructor,
            section_num,
        )

    def test_course_info_invalid_section_num(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        subject, course_num, instructor, section_num = (
            "cs",
            "0441",
            "GARRISON III",
            "12456",
        )

        self.assertRaises(
            ValueError,
            textbook.CourseInfo,
            subject,
            course_num,
            instructor,
            section_num,
        )

    @mark.filterwarnings("ignore:Attempt")
    @responses.activate
    def test_course_info_failing_header_requests(self):
        self.mock_base_site_failure()

        self.assertRaises(
            ConnectionError,
            textbook.CourseInfo,
            "CS",
            "0441",
            instructor="GARRISON III",
        )

    @responses.activate
    def test_course_info_no_headers(self):
        responses.add(
            responses.GET,
            "https://pitt.verbacompare.com/",
            body="<!DOCTYPE html><html lang='en-US'></html>",
        )

        self.assertRaises(
            ConnectionError,
            textbook.CourseInfo,
            "CS",
            "0441",
            instructor="GARRISON III",
        )

    @mark.filterwarnings("ignore:Attempt")
    @responses.activate
    def test_course_info_failing_subject_map_requests(self):
        self.mock_base_site_success()
        self.mock_subject_map_failure()

        self.assertRaises(
            ConnectionError,
            textbook.CourseInfo,
            "CS",
            "0441",
            instructor="GARRISON III",
        )

    def test_textbook_from_json(self):
        self.assertEqual(len(self.cs_0441_textbook_data), 1)

        textbook_info = textbook.Textbook.from_json(self.cs_0441_textbook_data[0])

        self.assertIsNotNone(textbook_info)
        self.assertEqual(textbook_info.title, "Ia Canvas Content")
        self.assertEqual(textbook_info.author, "Redshelf Ia")
        self.assertIsNone(textbook_info.edition)
        self.assertEqual(textbook_info.isbn, "BSZWEWZWMZYJ")
        self.assertEqual(
            textbook_info.citation,
            "<em>Ia Canvas Content</em> by Redshelf Ia. (ISBN: BSZWEWZWMZYJ).",
        )

    def test_textbook_from_json_all_empty(self):
        emptied_data: dict[str, Any] = self.cs_0441_textbook_data[0].copy()
        emptied_data.pop("title")
        emptied_data.pop("author")
        emptied_data.pop("edition")
        emptied_data.pop("isbn")
        emptied_data.pop("citation")

        textbook_info = textbook.Textbook.from_json(emptied_data)

        self.assertIsNone(textbook_info)

    @responses.activate
    def test_get_textbooks_for_course_section_num(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_cs_0441_garrison_books_success()
        course = textbook.CourseInfo("CS", "0441", section_num="1245")

        textbooks = textbook.get_textbooks_for_course(course)

        self.assertEqual(textbook.request_headers, {"X-CSRF-Token": CSRF_TOKEN})
        self.assertEqual(len(textbook.subject_map), 168)
        self.assertEqual(textbook.subject_map["CS"], CS_SUBJECT_ID)
        self.assertEqual(len(textbooks), 1)
        self.assertEqual(textbooks[0].title, "Ia Canvas Content")
        self.assertEqual(textbooks[0].author, "Redshelf Ia")
        self.assertIsNone(textbooks[0].edition)
        self.assertEqual(textbooks[0].isbn, "BSZWEWZWMZYJ")
        self.assertEqual(
            textbooks[0].citation,
            "<em>Ia Canvas Content</em> by Redshelf Ia. (ISBN: BSZWEWZWMZYJ).",
        )

    @responses.activate
    def test_get_textbooks_for_course_invalid_section_num(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_cs_0441_garrison_books_success()
        course = textbook.CourseInfo("CS", "0441", section_num="0000")

        self.assertRaises(LookupError, textbook.get_textbooks_for_course, course)

    @responses.activate
    def test_get_textbooks_for_course_instructor(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_cs_0441_garrison_books_success()
        course = textbook.CourseInfo("CS", "0441", instructor="GARRISON III")

        textbooks = textbook.get_textbooks_for_course(course)

        self.assertEqual(textbook.request_headers, {"X-CSRF-Token": CSRF_TOKEN})
        self.assertEqual(len(textbook.subject_map), 168)
        self.assertEqual(textbook.subject_map["CS"], CS_SUBJECT_ID)
        self.assertEqual(len(textbooks), 1)
        self.assertEqual(textbooks[0].title, "Ia Canvas Content")
        self.assertEqual(textbooks[0].author, "Redshelf Ia")
        self.assertIsNone(textbooks[0].edition)
        self.assertEqual(textbooks[0].isbn, "BSZWEWZWMZYJ")
        self.assertEqual(
            textbooks[0].citation,
            "<em>Ia Canvas Content</em> by Redshelf Ia. (ISBN: BSZWEWZWMZYJ).",
        )

    @responses.activate
    def test_get_textbooks_for_course_invalid_instructor(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_cs_0441_garrison_books_success()
        course = textbook.CourseInfo("CS", "0441", instructor="RAMIREZ")

        self.assertRaises(LookupError, textbook.get_textbooks_for_course, course)

    @responses.activate
    def test_get_textbooks_for_course_invalid_course(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        course = textbook.CourseInfo("CS", "0000")

        self.assertRaises(LookupError, textbook.get_textbooks_for_course, course)

    @responses.activate
    def test_get_textbooks_for_course_deduce_section(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_math_courses_success()
        self.mock_math_0430_pan_books_success()
        course = textbook.CourseInfo("MATH", "0430")

        textbooks = textbook.get_textbooks_for_course(course)

        self.assertEqual(len(textbooks), 1)
        self.assertEqual(textbooks[0].title, "First Course In Abstract Algebra")
        self.assertEqual(textbooks[0].author, "Fraleigh")
        self.assertEqual(textbooks[0].edition, "7")
        self.assertEqual(textbooks[0].isbn, "9780201763904")
        self.assertEqual(
            textbooks[0].citation,
            "\u003cem\u003eFirst Course In Abstract Algebra\u003c/em\u003e by Fraleigh. "
            "Pearson Education, 7th Edition, 2002. (ISBN: 9780201763904).",
        )

    @responses.activate
    def test_get_textbooks_for_course_not_enough_info(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        course = textbook.CourseInfo("CS", "0441")

        self.assertRaises(LookupError, textbook.get_textbooks_for_course, course)

    @mark.filterwarnings("ignore:Attempt")
    @responses.activate
    def test_get_textbooks_for_course_failing_courses_requests(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_failure()
        course = textbook.CourseInfo("CS", "0441", instructor="GARRISON III")

        self.assertRaises(ConnectionError, textbook.get_textbooks_for_course, course)

    @responses.activate
    def test_get_textbooks_for_course_no_textbook(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_cs_0441_garrison_books_none()
        course = textbook.CourseInfo("CS", "0441", instructor="GARRISON III")

        textbooks = textbook.get_textbooks_for_course(course)

        self.assertEqual(len(textbooks), 0)

    @mark.filterwarnings("ignore:No textbook info found")
    @responses.activate
    def test_get_textbooks_for_course_textbook_no_info(self):
        emptied_data: dict[str, Any] = self.cs_0441_textbook_data[0].copy()
        emptied_data.pop("title")
        emptied_data.pop("author")
        emptied_data.pop("edition")
        emptied_data.pop("isbn")
        emptied_data.pop("citation")
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        responses.add(
            responses.GET,
            f"https://pitt.verbacompare.com/compare/books?id={CS_0441_GARRISON_SECTION_ID}",
            json=[emptied_data],
        )
        course = textbook.CourseInfo("CS", "0441", instructor="GARRISON III")

        textbook_info = textbook.get_textbooks_for_course(course)

        self.assertEqual(len(textbook_info), 0)

    @responses.activate
    def test_get_textbooks_for_courses(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_success()
        self.mock_math_courses_success()
        self.mock_cs_0441_garrison_books_success()
        self.mock_math_0430_pan_books_success()
        courses = [
            textbook.CourseInfo("CS", "0441", instructor="GARRISON III"),
            textbook.CourseInfo("MATH", "0430", instructor="PAN"),
        ]

        textbooks = textbook.get_textbooks_for_courses(courses)

        self.assertEqual(len(textbooks), 2)
        # Sort to guarantee output order, since the textbook requests are async
        textbooks.sort(key=lambda x: x.author if x.author else "")

        self.assertEqual(textbooks[0].title, "First Course In Abstract Algebra")
        self.assertEqual(textbooks[0].author, "Fraleigh")
        self.assertEqual(textbooks[0].edition, "7")
        self.assertEqual(textbooks[0].isbn, "9780201763904")
        self.assertEqual(
            textbooks[0].citation,
            "\u003cem\u003eFirst Course In Abstract Algebra\u003c/em\u003e by Fraleigh. "
            "Pearson Education, 7th Edition, 2002. (ISBN: 9780201763904).",
        )

        self.assertEqual(textbooks[1].title, "Ia Canvas Content")
        self.assertEqual(textbooks[1].author, "Redshelf Ia")
        self.assertIsNone(textbooks[1].edition)
        self.assertEqual(textbooks[1].isbn, "BSZWEWZWMZYJ")
        self.assertEqual(
            textbooks[1].citation,
            "<em>Ia Canvas Content</em> by Redshelf Ia. (ISBN: BSZWEWZWMZYJ).",
        )

    @mark.filterwarnings("ignore:Attempt")
    @responses.activate
    def test_get_textbooks_for_courses_failing_courses_requests(self):
        self.mock_base_site_success()
        self.mock_subject_map_success()
        self.mock_cs_courses_failure()
        self.mock_math_courses_failure()
        courses = [
            textbook.CourseInfo("CS", "0441", instructor="GARRISON III"),
            textbook.CourseInfo("MATH", "0430", instructor="PAN"),
        ]

        self.assertRaises(ConnectionError, textbook.get_textbooks_for_courses, courses)

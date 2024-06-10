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
import json
import unittest

from pathlib import Path

from pittapi import textbook

TERM = "1000"
SAMPLE_PATH = Path() / "tests" / "samples"

print(SAMPLE_PATH.absolute())


class TextbookTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.validate_term = textbook._validate_term
        self.validate_course = textbook._validate_course
        with (SAMPLE_PATH / "textbook_courses_CS.json").open() as f:
            self.cs_data = json.load(f)
        with (SAMPLE_PATH / "textbook_courses_STAT.json").open() as f:
            self.stat_data = json.load(f)

    @responses.activate
    def test_textbook_get_textbook(self):
        responses.add(
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        instructor_test = textbook.get_textbook(
            term=TERM, department="CS", course="445", instructor="GARRISON III"
        )
        instructor_test = textbook.get_textbook(term=TERM, department="CS", course="445", instructor="GARRISON III")

        section_test = textbook.get_textbook(
            term=TERM, department="CS", course="445", section="1030"
        )
        self.assertIsInstance(instructor_test, list)
        self.assertIsInstance(section_test, list)

    @responses.activate
    def test_textbook_get_textbooks(self):
        responses.add(
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        responses.add(
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22594&term_id=1000",
            json=self.stat_data,
            status=200,
        )
        multi_book_test = textbook.get_textbooks(
            term=TERM,
            courses=[
                {"department": "STAT", "course": "1000", "instructor": "WANG"},
                {"department": "CS", "course": "445", "section": "1030"},
            ],
        )
        self.assertIsInstance(multi_book_test, list)

    @responses.activate
    def test_get_textbook_invalid_term(self):
        responses.add(
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        self.assertRaises(TypeError, textbook.get_textbook, "0000", "CS", "401")

    @responses.activate
    def test_get_textbook_invalid_subject(self):
        # TODO(@azharichenko): Added better subject verification in future update
        responses.add(
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        self.assertRaises(
            ValueError,
            textbook.get_textbook,
            TERM,
            "Computer Science",
            "000",
            "EXIST",
            None,
        )
    @responses.activate
    def test_get_textbook_invalid_instructor(self):
        responses.add(
<<<<<<< HEAD
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        self.assertRaises(
            LookupError, textbook.get_textbook, TERM, "CS", "447", "EXIST", None
        )
=======
            responses.GET, "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000", json=self.cs_data, status=200
        )
        self.assertRaises(LookupError, textbook.get_textbook, TERM, "CS", "447", "EXIST", None)
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6

    @responses.activate
    def test_get_textbook_invalid_section(self):
        responses.add(
<<<<<<< HEAD
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        self.assertRaises(
            LookupError, textbook.get_textbook, TERM, "CS", "401", None, "9999"
        )
=======
            responses.GET, "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000", json=self.cs_data, status=200
        )
        self.assertRaises(LookupError, textbook.get_textbook, TERM, "CS", "401", None, "9999")
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6

    @responses.activate
    def test_get_textbook_invalid_section_and_instructor(self):
        responses.add(
<<<<<<< HEAD
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=200,
        )
        self.assertRaises(
            TypeError, textbook.get_textbook, TERM, "CS", "401", None, None
        )
=======
            responses.GET, "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000", json=self.cs_data, status=200
        )
        self.assertRaises(TypeError, textbook.get_textbook, TERM, "CS", "401", None, None)
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6

    def test_term_validation(self):
        self.assertEqual(self.validate_term(TERM), TERM)

    def test_term_validation_invalid(self):
        self.assertRaises(ValueError, self.validate_term, "1")
        self.assertRaises(ValueError, self.validate_term, "a")
        self.assertRaises(ValueError, self.validate_term, "100")
        self.assertRaises(ValueError, self.validate_term, "10000")

    def test_validate_course_correct_input(self):
        self.assertEqual(self.validate_course("0000"), "0000")
        self.assertEqual(self.validate_course("0001"), "0001")
        self.assertEqual(self.validate_course("0012"), "0012")
        self.assertEqual(self.validate_course("0123"), "0123")
        self.assertEqual(self.validate_course("1234"), "1234")
        self.assertEqual(self.validate_course("9999"), "9999")

    def test_validate_course_improper_input(self):
        self.assertEqual(self.validate_course("0"), "0000")
        self.assertEqual(self.validate_course("1"), "0001")
        self.assertEqual(self.validate_course("12"), "0012")
        self.assertEqual(self.validate_course("123"), "0123")

    def test_validate_course_incorrect_input(self):
        self.assertRaises(ValueError, self.validate_course, "")
        self.assertRaises(ValueError, self.validate_course, "00000")
        self.assertRaises(ValueError, self.validate_course, "11111")
        self.assertRaises(ValueError, self.validate_course, "hi")

    def test_construct_query(self):
        construct = textbook._construct_query
        course_query = "compare/courses/?id=9999&term_id=1111"
        book_query = "compare/books?id=9999"

        self.assertEqual(construct("courses", "9999", "1111"), course_query)
        self.assertEqual(construct("books", "9999"), book_query)

    def test_find_item(self):
        find = textbook._find_item("id", "key", "test")
<<<<<<< HEAD
        test_data = [
            {"id": 1, "key": 1},
            {"id": 2, "key": 4},
            {"id": 3, "key": 9},
            {"id": 4, "key": 16},
            {"id": 5, "key": 25},
        ]
=======
        test_data = [{"id": 1, "key": 1}, {"id": 2, "key": 4}, {"id": 3, "key": 9}, {"id": 4, "key": 16}, {"id": 5, "key": 25}]
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6

        for i in range(1, 6):
            self.assertEqual(find(test_data, i), i**2)

        self.assertRaises(LookupError, find, test_data, 6)

    @responses.activate
    def test_extract_id(self):
        responses.add(
<<<<<<< HEAD
            responses.GET,
            "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000",
            json=self.cs_data,
            status=201,
=======
            responses.GET, "http://pitt.verbacompare.com/compare/courses/?id=22457&term_id=1000", json=self.cs_data, status=201
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6
        )

    def test_filter_dictionary(self):
        test_dict = {"a": 1, "b": 2, "c": 3}
        test_key = ["a", "c"]
<<<<<<< HEAD
        self.assertEqual(
            textbook._filter_dictionary(test_dict, test_key), {"a": 1, "c": 3}
        )

    def test_invalid_department_code(self):
        self.assertRaises(
            ValueError, textbook.get_textbook, TERM, "TEST", "000", "EXIST", None
        )
=======
        self.assertEqual(textbook._filter_dictionary(test_dict, test_key), {"a": 1, "c": 3})

    def test_invalid_department_code(self):
        self.assertRaises(ValueError, textbook.get_textbook, TERM, "TEST", "000", "EXIST", None)
>>>>>>> 5707e24e2f881755bb429b3b1a0f2245940b46d6

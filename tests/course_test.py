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

import unittest
from unittest.mock import MagicMock

from pittapi import course

from pittapi.course import (
    Attribute,
    Component,
    Course,
    CourseDetails,
    Instructor,
    Meeting,
    Section,
    SectionDetails,
    Subject,
)

from tests.mocks.course_mocks import (
    mocked_subject_data,
    mocked_courses_data,
    mocked_courses_data_invalid,
    mocked_course_info_data,
    mocked_course_sections_data,
    mocked_section_details_data,
)


class CourseTest(unittest.TestCase):
    def setUp(self):
        course._get_subjects = MagicMock(return_value=mocked_subject_data)
        course._get_section_details = MagicMock(return_value=mocked_section_details_data)

    def test_validate_term(self):
        # If convert to string
        self.assertTrue(isinstance(course._validate_term(2191), str))

        self.assertEqual(course._validate_term(2191), "2191")
        self.assertEqual(course._validate_term("2191"), "2191")

        self.assertRaises(ValueError, course._validate_term, "214")
        self.assertRaises(ValueError, course._validate_term, "1111")
        self.assertRaises(ValueError, course._validate_term, "12345")

    def test_validate_subject(self):
        self.assertEqual(course._validate_subject("CS"), "CS")

        self.assertRaises(ValueError, course._validate_subject, "foobar")

    def test_validate_course(self):
        self.assertEqual(course._validate_course(7), "0007")
        self.assertEqual(course._validate_course(449), "0449")
        self.assertEqual(course._validate_course(1501), "1501")

        self.assertEqual(course._validate_course("7"), "0007")
        self.assertEqual(course._validate_course("0007"), "0007")
        self.assertEqual(course._validate_course("449"), "0449")
        self.assertEqual(course._validate_course("1501"), "1501")

        self.assertRaises(ValueError, course._validate_course, -1)
        self.assertRaises(ValueError, course._validate_course, 0)
        self.assertRaises(ValueError, course._validate_course, "")
        self.assertRaises(ValueError, course._validate_course, "A00")
        self.assertRaises(ValueError, course._validate_course, "Hello")
        self.assertRaises(ValueError, course._validate_course, "10000")

    def test_get_subject_courses(self):
        course._get_subject_courses = MagicMock(return_value=mocked_courses_data)

        subject_courses = course.get_subject_courses("CS")

        course._get_subject_courses.assert_called_once_with("CS")

        self.assertTrue(isinstance(subject_courses, Subject))

        self.assertEqual(len(subject_courses.courses), 1)
        self.assertTrue("0007" in subject_courses.courses)
        test_course = subject_courses.courses["0007"]
        self.assertTrue(isinstance(test_course, Course))

    def test_get_subject_courses_invalid(self):
        course._get_subject_courses = MagicMock(return_value=mocked_courses_data_invalid)

        self.assertRaises(ValueError, course.get_subject_courses, "nonsense")
        course._get_subject_courses.assert_not_called()

    def test_get_course_details(self):
        course._get_course_id = MagicMock(return_value="105611")
        course._get_course_info = MagicMock(return_value=mocked_course_info_data)
        course._get_course_sections = MagicMock(return_value=mocked_course_sections_data)

        course_sections = course.get_course_details("2231", "CS", "0007")

        self.assertTrue(isinstance(course_sections, CourseDetails))

        self.assertTrue(isinstance(course_sections.course, Course))
        course_obj = course_sections.course
        self.assertEqual(course_obj.subject_code, "CS")
        self.assertEqual(course_obj.course_number, "0007")
        self.assertEqual(course_obj.course_id, "105611")
        self.assertEqual(course_obj.course_title, "INTRO TO COMPUTER PROGRAMMING")

        self.assertEqual(len(course_sections.sections), 1)
        test_attribute = course_sections.attributes[0]
        self.assertTrue(isinstance(test_attribute, Attribute))
        self.assertEqual(test_attribute.attribute, "DSGE")
        self.assertEqual(test_attribute.attribute_description, "*DSAS General Ed. Requirements")
        self.assertEqual(test_attribute.value, "ALG")
        self.assertEqual(test_attribute.value_description, "Algebra")
        test_section = course_sections.sections[0]
        self.assertTrue(isinstance(test_section, Section))
        self.assertEqual(test_section.term, "2231")
        self.assertEqual(test_section.session, "Academic Term")
        self.assertEqual(test_section.section_number, "1000")
        self.assertEqual(test_section.class_number, "27815")
        self.assertEqual(test_section.section_type, "REC")
        self.assertEqual(test_section.status, "Open")

        self.assertEqual(len(test_section.instructors), 1)
        self.assertEqual(len(test_section.meetings), 1)
        test_instructor = test_section.instructors[0]
        test_meeting = test_section.meetings[0]
        self.assertTrue(isinstance(test_instructor, Instructor))
        self.assertEqual(test_instructor.name, "Robert Fishel")
        self.assertEqual(test_instructor.email, "rmf105@pitt.edu")
        self.assertTrue(isinstance(test_meeting, Meeting))
        self.assertEqual(test_meeting.days, "Fr")
        self.assertEqual(test_meeting.start_time, "10.00.00.000000-05:00")
        self.assertEqual(test_meeting.end_time, "10.50.00.000000-05:00")
        self.assertEqual(test_meeting.start_date, "08/29/2022")
        self.assertEqual(test_meeting.end_date, "12/09/2022")

        test_instructor = test_section.instructors[0]
        self.assertTrue(isinstance(test_instructor, Instructor))
        self.assertEqual(test_instructor.name, "Robert Fishel")

    def test_get_section_details(self):
        course._get_section_details = MagicMock(return_value=mocked_section_details_data)

        section_details = course.get_section_details("2231", "27815")

        self.assertTrue(isinstance(section_details, Section))
        self.assertEqual(section_details.term, "2231")
        self.assertEqual(section_details.session, "Academic Term")
        self.assertEqual(section_details.class_number, "27815")
        self.assertEqual(section_details.section_type, "REC")
        self.assertEqual(section_details.status, "Open")
        self.assertIsNone(section_details.instructors)
        test_meeting = section_details.meetings[0]

        self.assertTrue(isinstance(test_meeting, Meeting))
        self.assertEqual(test_meeting.days, "Fr")
        self.assertEqual(test_meeting.start_time, "10:00AM")
        self.assertEqual(test_meeting.end_time, "10:50AM")
        self.assertEqual(test_meeting.start_date, "08/29/2022")
        self.assertEqual(test_meeting.end_date, "12/09/2022")
        test_instructor = test_meeting.instructors[0]

        self.assertTrue(isinstance(test_instructor, Instructor))
        self.assertEqual(test_instructor.name, "Robert Fishel")
        self.assertEqual(test_instructor.email, "rmf105@pitt.edu")

        test_details = section_details.details
        self.assertTrue(isinstance(test_details, SectionDetails))
        self.assertEqual(test_details.units, "0 units")
        self.assertEqual(test_details.class_capacity, "28")
        self.assertEqual(test_details.enrollment_total, "24")
        self.assertEqual(test_details.enrollment_available, "4")
        self.assertEqual(test_details.wait_list_capacity, "50")
        self.assertEqual(test_details.wait_list_total, "7")
        self.assertEqual(test_details.valid_to_enroll, "T")
        self.assertIsNone(test_details.combined_section_numbers)

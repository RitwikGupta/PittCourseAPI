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

import datetime
import re
import requests
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

# https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UPITT&term=2244&date_from=&date_thru=&subject=CS&subject_like=&catalog_nbr=&time_range=&days=&campus=PIT&location=&x_acad_career=UGRD&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=O&crse_attr=&crse_attr_value=&instructor_name=&instr_first_name=&session_code=&units=&trigger_search=&page=1
SUBJECTS_API = "https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_CatalogSubjects?institution=UPITT"
SUBJECT_COURSES_API = "https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_SubjectCourses?institution=UPITT&subject={subject}"
COURSE_DETAIL_API = "https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_CatalogCourseDetails?institution=UPITT&course_id={id}&effdt=2018-06-30&crse_offer_nbr=1&use_catalog_print=Y"
COURSE_SECTIONS_API = "https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_BROWSE_CLASSES.FieldFormula.IScript_BrowseSections?institution=UPITT&campus=&location=&course_id={id}&institution=UPITT&term={term}&crse_offer_nbr=1"
SECTION_DETAILS_API = "https://pitcsprd.csps.pitt.edu/psc/pitcsprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassDetails?institution=UPITT&term={term}&class_nbr={id}"
# id -> unique course ID, not to be confused with course code (for instance, CS 0007 has code 105611)
# career -> for example, UGRD (undergraduate)

TERM_REGEX = "2\d\d[147]"
VALID_TERMS = re.compile(TERM_REGEX)


class Instructor(NamedTuple):
    name: str
    email: Optional[str] = None


class Meeting(NamedTuple):
    days: str
    start_time: str
    end_time: str
    start_date: str
    end_date: str
    instructors: Optional[List[Instructor]] = None


class Attribute(NamedTuple):
    attribute: str
    attribute_description: str
    value: str
    value_description: str


class Component(NamedTuple):
    component: str
    required: bool


class SectionDetails(NamedTuple):
    units: str

    class_capacity: str
    enrollment_total: str
    enrollment_available: str
    wait_list_capacity: str
    wait_list_total: str
    valid_to_enroll: str

    combined_section_numbers: Optional[List[str]] = None


class Section(NamedTuple):
    term: str
    session: str
    section_number: str
    class_number: str
    section_type: str
    status: str
    instructors: Optional[List[Instructor]] = None
    meetings: Optional[List[Meeting]] = None
    details: Optional[SectionDetails] = None


class Course(NamedTuple):
    subject_code: str
    course_number: str
    course_id: str
    course_title: str


class CourseDetails(NamedTuple):
    course: Course
    course_description: Optional[str] = None
    credit_range: Optional[Tuple[int]] = None
    requisites: Optional[str] = None
    components: List[Component] = None
    attributes: List[Attribute] = None
    sections: Optional[List[Section]] = None


class Subject(NamedTuple):
    subject_code: str
    courses: Dict[str, Course]


def get_subject_courses(subject: str) -> Subject:
    subject = _validate_subject(subject)

    json_response = _get_subject_courses(subject)

    courses = {}
    for course in json_response["courses"]:
        course_number = course["catalog_nbr"]
        course_id = course["crse_id"]
        course_title = course["descr"]

        course_obj = Course(
            subject_code=subject,
            course_number=course_number,
            course_id=course_id,
            course_title=course_title,
        )

        courses[course_number] = course_obj

    return Subject(subject_code=subject, courses=courses)


def get_course_details(term: Union[str, int], subject: str, course: Union[str, int]) -> CourseDetails:
    term = _validate_term(term)
    subject = _validate_subject(subject)
    course = _validate_course(course)

    internal_course_id = _get_course_id(subject, course)
    json_response = _get_course_info(internal_course_id)["course_details"]
    json_response_details = _get_course_sections(internal_course_id, term)

    course_title = json_response_details["sections"][0]["descr"]
    course_description = json_response["descrlong"]
    credit_range = (json_response["units_minimum"], json_response["units_maximum"])

    requisites = None
    if "offerings" in json_response and len(json_response["offerings"]) != 0 and "req_group" in json_response["offerings"][0]:
        requisites = json_response["offerings"][0]["req_group"]

    components = None
    if "components" in json_response and len(json_response["components"]) != 0:
        components = []
        for component in json_response["components"]:
            components.append(
                Component(
                    component=component["descr"],
                    required=True if component["optional"] == "N" else False,
                )
            )

    attributes = None
    if "attributes" in json_response and len(json_response["attributes"]) != 0:
        attributes = []
        for attribute in json_response["attributes"]:
            attributes.append(
                Attribute(
                    attribute=attribute["crse_attribute"],
                    attribute_description=attribute["crse_attribute_descr"],
                    value=attribute["crse_attribute_value"],
                    value_description=attribute["crse_attribute_value_descr"],
                )
            )

    sections = []
    for section in json_response_details["sections"]:
        session = section["session"]
        section_number = section["class_section"]
        class_number = str(section["class_nbr"])
        section_type = section["section_type"]
        status = section["enrl_stat_descr"]

        instructors = None
        if len(section["instructors"]) != 0 and section["instructors"][0] != "To be Announced":
            instructors = []
            for instructor in section["instructors"]:
                instructors.append(Instructor(name=instructor["name"], email=instructor["email"]))

        meetings = None
        if len(section["meetings"]) != 0:
            meetings = []
            for meeting in section["meetings"]:
                meetings.append(
                    Meeting(
                        days=meeting["days"],
                        start_time=meeting["start_time"],
                        end_time=meeting["end_time"],
                        start_date=meeting["start_dt"],
                        end_date=meeting["end_dt"],
                        instructors=[Instructor(name=meeting["instructor"])],
                    )
                )

        sections.append(
            Section(
                term=term,
                session=session,
                section_number=section_number,
                class_number=class_number,
                section_type=section_type,
                status=status,
                instructors=instructors,
                meetings=meetings,
            )
        )

    return CourseDetails(
        course=Course(subject_code=subject, course_number=course, course_id=internal_course_id, course_title=course_title),
        course_description=course_description,
        credit_range=credit_range,
        requisites=requisites,
        components=components,
        attributes=attributes,
        sections=sections,
    )


def get_section_details(term: Union[str, int], class_number: Union[str, int]) -> Section:
    term = _validate_term(term)

    json_response = _get_section_details(term, class_number)
    details = json_response["section_info"]["class_details"]
    meetings = json_response["section_info"]["meetings"]
    enrollment = json_response["section_info"]["class_availability"]

    session = details["session"]
    section_num = details["class_section"]
    section_type = details["component"]
    status = details["status"]

    meeting_objs = None
    if len(meetings) != 0:
        meeting_objs = []
        for meeting in meetings:
            days = meeting["days"]
            start_time = meeting["meeting_time_start"]
            end_time = meeting["meeting_time_end"]
            # start_date = meeting["start_date"]
            # end_date = meeting["end_date"]
            date_range = meeting["date_range"].split(" - ")

            instructors = None
            if len(meeting["instructors"]) != 0 and meeting["instructors"][0]["name"] not in ["To be Announced", "-"]:
                instructors = []
                for instructor in meeting["instructors"]:
                    name = instructor["name"]
                    email = instructor["email"]

                    instructors.append(Instructor(name=name, email=email))

            meeting_objs.append(
                Meeting(
                    days=days,
                    start_time=start_time,
                    end_time=end_time,
                    start_date=date_range[0],
                    end_date=date_range[1],
                    instructors=instructors,
                )
            )

    units = details["units"]
    class_capacity = enrollment["class_capacity"]
    enrollment_total = enrollment["enrollment_total"]
    enrollment_available = str(enrollment["enrollment_available"])
    wait_list_capacity = enrollment["wait_list_capacity"]
    wait_list_total = enrollment["wait_list_total"]
    valid_to_enroll = json_response["section_info"]["valid_to_enroll"]
    combined_section_numbers = None
    if json_response["section_info"]["is_combined"]:
        combined_section_numbers = []
        for section in json_response["section_info"]["combined_sections"]:
            combined_section_numbers.append(section["class_nbr"])

    details = SectionDetails(
        units=units,
        class_capacity=class_capacity,
        enrollment_total=enrollment_total,
        enrollment_available=enrollment_available,
        wait_list_capacity=wait_list_capacity,
        wait_list_total=wait_list_total,
        valid_to_enroll=valid_to_enroll,
        combined_section_numbers=combined_section_numbers,
    )

    return Section(
        term=term,
        session=session,
        section_number=section_num,
        class_number=str(class_number),
        section_type=section_type,
        status=status,
        instructors=None,
        meetings=meeting_objs,
        details=details,
    )


# validation for method inputs
def _validate_term(term: Union[str, int]) -> str:
    """Validates that the term entered follows the pattern that Pitt does for term codes."""
    if VALID_TERMS.match(str(term)):
        return str(term)
    raise ValueError("Term entered isn't a valid Pitt term, must match regex " + TERM_REGEX)


def _validate_subject(subject: str) -> str:
    """Validates that the subject code entered is present in the API request."""
    if subject in _get_subject_codes():
        return subject
    raise ValueError("Subject code entered isn't a valid Pitt subject code.")


def _validate_course(course: Union[str, int]) -> str:
    """Validates that the course name entered is 4 characters long and in string form."""
    if course == "":
        raise ValueError("Invalid course number, please enter a non-empty string.")
    if (type(course) is str) and (not course.isdigit()):
        raise ValueError("Invalid course number, must be a number")
    if (type(course) is int) and (course <= 0):
        raise ValueError("Invalid course number, must be positive")
    course_length = len(str(course))
    if course_length < 4:
        return ("0" * (4 - course_length)) + str(course)
    elif course_length > 4:
        raise ValueError("Invalid course number, must be 4 characters long")
    return str(course)


# peoplesoft api calls
def _get_subjects() -> dict:
    return requests.get(SUBJECTS_API).json()


def _get_subject_courses(subject: str) -> dict:
    return requests.get(SUBJECT_COURSES_API.format(subject=subject)).json()


def _get_course_info(course_id: str) -> dict:
    response = requests.get(COURSE_DETAIL_API.format(id=course_id)).json()
    if response["course_details"] == {}:
        raise ValueError("Invalid course ID; course with that ID does not exist")
    return response


def _get_course_sections(course_id: str, term: str) -> dict:
    response = requests.get(COURSE_SECTIONS_API.format(id=course_id, term=term)).json()
    if len(response["sections"]) == 0:
        raise ValueError("Invalid course ID; course with that ID does not exist")
    return response


def _get_section_details(term: str, section_id: str) -> dict:
    response = requests.get(SECTION_DETAILS_API.format(term=term, id=section_id)).json()
    if "error" in response:
        raise ValueError("Invalid section ID; section with that ID does not exist")
    return response


# operations from api calls
def _get_subject_codes() -> List[str]:
    response = _get_subjects()
    codes = []
    for subject in response["subjects"]:
        codes.append(subject["subject"])
    return codes


def _get_internal_id_dict(subject: str) -> dict:
    response = _get_subject_courses(subject)
    internal_id_dict = {}
    for course in response["courses"]:
        if course["catalog_nbr"] not in internal_id_dict:
            internal_id_dict[course["catalog_nbr"]] = course["crse_id"]
    return internal_id_dict


def _get_course_id(subject: str, course: str) -> str:
    subject_dict = _get_internal_id_dict(subject)
    if str(course) not in subject_dict:
        raise ValueError("No course with that number within listed subject")
    return subject_dict[str(course)]

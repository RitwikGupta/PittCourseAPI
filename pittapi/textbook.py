from __future__ import annotations

# grequests must be imported before all other libraries, especially requests,
# because grequests uses gevent, which in turn uses monkey-patching to implement concurrency
import grequests
import warnings

from dataclasses import dataclass
from requests import ConnectionError
from requests_html import HTMLResponse, HTMLSession
from typing import Any, NamedTuple

BASE_URL = "https://pitt.verbacompare.com/"

SUBJECTS_URL = BASE_URL + "compare/departments/?term={term_id}"
COURSES_URL = BASE_URL + "compare/courses/?id={dept_id}&term_id={term_id}"
BOOKS_URL = BASE_URL + "compare/books?id={section_id}"

CURRENT_TERM_ID = 78104  # Term ID for fall 2024, TODO: figure out how this ID is generated
MAX_REQUEST_ATTEMPTS = 3

sess = HTMLSession()
request_headers: dict[str, str] | None = None
subject_map: dict[str, str] | None = None


@dataclass  # No dataclass slots because they're not supported in Python 3.9
class CourseInfo:
    subject: str
    course_num: str
    instructor: str | None = None
    section_num: str | None = None

    def __post_init__(self) -> None:
        if not subject_map:
            _update_subject_map()
            assert subject_map

        self.subject = self.subject.upper()
        if self.subject not in subject_map:
            raise LookupError(f"{self.subject} is not a valid subject")
        if len(self.course_num) > 4 or not self.course_num.isdigit():
            raise ValueError("Invalid course number")
        self.course_num = "0" * (4 - len(self.course_num)) + self.course_num
        if self.instructor:
            self.instructor = self.instructor.upper()
        if self.section_num and (len(self.section_num) != 4 or not self.section_num.isdigit()):
            raise ValueError("Invalid section number")


class Textbook(NamedTuple):
    title: str | None
    author: str | None
    edition: str | None
    isbn: str | None
    citation: str | None

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Textbook | None:
        parsed_textbook = cls(
            title=json.get("title"),
            author=json.get("author"),
            edition=json.get("edition"),
            isbn=json.get("isbn"),
            citation=json.get("citation"),
        )
        # If all fields are None, then don't bother returning a Textbook object
        return parsed_textbook if any(field for field in parsed_textbook) else None


def _update_headers() -> None:
    for i in range(MAX_REQUEST_ATTEMPTS):
        base_response: HTMLResponse = sess.get(BASE_URL)
        if base_response.status_code == 200:
            break
        warnings.warn(f"Attempt {i + 1} to connect to textbook site failed, trying again")
    if base_response.status_code != 200:  # Request failed too many times
        raise ConnectionError(f"Failed to connect to textbook site after {MAX_REQUEST_ATTEMPTS} attempts")

    elements = base_response.html.find("meta")
    assert isinstance(elements, list)
    for element in elements:
        if element.attrs.get("name") == "csrf-token":
            csrf_token: str = element.attrs["content"]
            global request_headers
            request_headers = {"X-CSRF-Token": csrf_token}
            return
    raise ConnectionError("Unable to find valid request credentials, cannot connect to textbook site")


def _update_subject_map() -> None:
    if not request_headers:
        _update_headers()

    for i in range(MAX_REQUEST_ATTEMPTS):
        subject_response = sess.get(SUBJECTS_URL.format(term_id=CURRENT_TERM_ID), headers=request_headers)
        if subject_response.status_code == 200:
            break
        warnings.warn(f"Attempt {i + 1} to retrieve list of subjects failed, trying again")
        _update_headers()  # Try again with new CSRF token
    if subject_response.status_code != 200:  # Request failed too many times
        raise ConnectionError(f"Failed to retrieve list of subjects after {MAX_REQUEST_ATTEMPTS} attempts")

    subject_json: list[dict[str, str]] = subject_response.json()
    global subject_map
    subject_map = {entry["name"]: entry["id"] for entry in subject_json}


def _find_section_from_json(sections: list[dict[str, str]], instructor: str | None, section_num: str | None) -> str:
    if section_num:
        for section in sections:
            if section["name"] == section_num:
                return section["id"]
        raise LookupError(f"No section found with given {section_num=}")
    if instructor:
        for section in sections:
            if section["instructor"] == instructor:
                return section["id"]
        raise LookupError(f"No section found with given {instructor=}")

    # Not enough info provided, so try to deduce the correct section:
    # - If there's only 1 section of the course, then the sole section must be the correct one
    # - If all sections of the course are taught by the same instructor, then we can assume that all sections will have the
    #   same textbook, meaning that the exact section doesn't matter
    instructors = {section["instructor"] for section in sections}
    if len(sections) == 1 or len(instructors) == 1:
        return sections[0]["id"]
    raise LookupError(
        "Cannot determine section ID from given arguments, please provide the instructor's name and/or the section number"
    )


def _get_textbooks_for_ids(ids: list[str]) -> list[Textbook]:
    """Fetches a course's textbook information and returns a list
    of textbooks for the given course.
    """
    if not request_headers:
        _update_headers()

    responses = grequests.imap(grequests.get(BOOKS_URL.format(section_id=id), headers=request_headers) for id in ids)
    books = []
    for response in responses:
        for book_json in response.json():
            book = Textbook.from_json(book_json)
            if book:
                books.append(book)
            else:
                warnings.warn(f"No textbook info found for {response}")
    return [book for book in books if book]  # Drop all None values


def _get_textbooks_from_json(
    course_json: list[dict[str, Any]], subject: str, course_num: str, instructor: str | None, section_num: str | None
) -> list[Textbook]:
    for course in course_json:
        if course["id"] == subject + course_num:
            section_id = _find_section_from_json(course["sections"], instructor, section_num)
            return _get_textbooks_for_ids([section_id])
    raise LookupError(f"{subject} {course_num} is not a valid course")


def get_textbooks_for_course(course: CourseInfo) -> list[Textbook]:
    if not request_headers:
        _update_headers()
    if not subject_map:
        _update_subject_map()
        assert subject_map

    for i in range(MAX_REQUEST_ATTEMPTS):
        course_response = sess.get(
            COURSES_URL.format(dept_id=subject_map[course.subject], term_id=CURRENT_TERM_ID), headers=request_headers
        )
        if course_response.status_code == 200:
            break
        warnings.warn(f"Attempt {i} to retrieve list of {course.subject} courses failed, trying again")
        _update_headers()  # Try again with new CSRF token
    if course_response.status_code != 200:  # Request failed too many times
        raise ConnectionError(f"Failed to retrieve list of {course.subject} courses from textbook site")

    return _get_textbooks_from_json(
        course_json=course_response.json(),
        subject=course.subject,
        course_num=course.course_num,
        instructor=course.instructor,
        section_num=course.section_num,
    )


def get_textbooks_for_courses(courses_info: list[CourseInfo]) -> list[Textbook]:
    if not request_headers:
        _update_headers()
    if not subject_map:
        _update_subject_map()
        assert subject_map

    # Precompute list of unique subjects to avoid unnecessary API requests
    subjects = {course_info.subject for course_info in courses_info}
    courses_for_subjects: dict[str, list[dict[str, Any]]] = {}
    for subject in subjects:
        for i in range(MAX_REQUEST_ATTEMPTS):
            course_response = sess.get(
                COURSES_URL.format(dept_id=subject_map[subject], term_id=CURRENT_TERM_ID), headers=request_headers
            )
            if course_response.status_code == 200:
                break
            warnings.warn(f"Attempt {i} to retrieve list {subject} courses failed, trying again")
            _update_headers()  # Try again with new CSRF token
        if course_response.status_code != 200:  # Request failed too many times
            raise ConnectionError(f"Failed to retrieve list of {subject} courses from textbook site")

        courses_for_subjects[subject] = course_response.json()

    textbooks = []
    for course_info in courses_info:
        course_json = courses_for_subjects[course_info.subject]
        textbooks.extend(
            _get_textbooks_from_json(
                course_json=course_json,
                subject=course_info.subject,
                course_num=course_info.course_num,
                instructor=course_info.instructor,
                section_num=course_info.section_num,
            )
        )
    return textbooks

mocked_subject_data = {"subjects": [{"subject": "CS", "descr": "Computer Science"}]}

mocked_courses_data = {
    "courses": [
        {
            "catalog_nbr": "0007",
            "descr": "INTRODUCTION TO COMPUTER PROGRAMMING",
            "crse_id": "105611",
        }
    ]
}

mocked_courses_data_invalid = {}

mocked_course_info_data = {
    "course_details": {
        "descrlong": "This is a first course in computer science programming. It is recommended for those students intending to major in computer science who do not have the required background for cs 0401. It may also be of interest to students majoring in one of the social sciences or humanities. The focus of the course is on problem analysis and the development of algorithms and computer programs in a modern high-level language.",
        "units_minimum": 3,
        "units_maximum": 3,
        "units_inc": 1,
        "grading_basis": "OP2",
        "grading_basis_descr": "LG/SNC Elective Basis",
        "course_title": "INTRODUCTION TO COMPUTER PROGRAMMING",
        "rqmnt_designtn": "",
        "effdt": "2018-06-30",
        "components": [
            {"descr": "Lecture", "optional": "N"},
            {"descr": "Recitation", "optional": "N"},
        ],
        "attributes": [
            {
                "crse_attribute": "DSGE",
                "crse_attribute_descr": "*DSAS General Ed. Requirements",
                "crse_attribute_value": "ALG",
                "crse_attribute_value_descr": "Algebra",
            },
            {
                "crse_attribute": "DSGE",
                "crse_attribute_descr": "*DSAS General Ed. Requirements",
                "crse_attribute_value": "QFR",
                "crse_attribute_value_descr": "Quant.-Formal Reasoning",
            },
        ],
        "offerings": [
            {
                "crse_offer_nbr": 1,
                "subject": "CS",
                "catalog_nbr": "0007",
                "acad_career": "Undergraduate",
                "acad_group": "Sch Computing and Information",
                "acad_org": "Computer Science",
                "campus": "Pittsburgh Campus",
                "campus_cd": "PIT",
                "req_group": "",
                "planner_message": "You have no active career, so you can not add this course to a planner.",
                "open_terms": [
                    {
                        "strm": "2224",
                        "descr": "Spring Term 2021-2022",
                        "default_term": False,
                    },
                    {
                        "strm": "2227",
                        "descr": "Summer Term 2021-2022",
                        "default_term": False,
                    },
                    {
                        "strm": "2231",
                        "descr": "Fall Term 2022-2023",
                        "default_term": True,
                    },
                ],
                "enrollable_terms": [
                    {"strm": "2224"},
                    {"strm": "2227"},
                    {"strm": "2231"},
                ],
            }
        ],
    }
}

mocked_course_sections_data = {
    "show_reserve_cap": True,
    "show_share": False,
    "mobile_url": "https://cs92-dev.mhighpoint.com",
    "sections": [
        {
            "combined_section": False,
            "enrl_stat": "O",
            "enrl_stat_descr": "Open",
            "crse_id": "105611",
            "crse_offer_nbr": 1,
            "crs_topic_id": 0,
            "descr": "INTRO TO COMPUTER PROGRAMMING",
            "subject": "CS",
            "catalog_nbr": "0007",
            "class_section": "1000",
            "class_nbr": 27815,
            "class_type": "N",
            "session_code": "AT",
            "session": "Academic Term",
            "schedule_print": "Y",
            "class_stat": "A",
            "wait_tot": 7,
            "wait_cap": 50,
            "class_capacity": 28,
            "enrollment_total": 24,
            "enrollment_available": 4,
            "component": "REC",
            "start_dt": "08/29/2022",
            "end_dt": "12/09/2022",
            "units": "0",
            "topic": "",
            "instructors": [{"name": "Robert Fishel", "email": "rmf105@pitt.edu"}],
            "section_type": "REC",
            "meetings": [
                {
                    "days": "Fr",
                    "start_time": "10.00.00.000000-05:00",
                    "end_time": "10.50.00.000000-05:00",
                    "start_dt": "08/29/2022",
                    "end_dt": "12/09/2022",
                    "instructor": "Robert Fishel",
                }
            ],
            "reserve_caps": [],
        }
    ],
}

mocked_section_details_data = {
    "show_validate": "N",
    "show_waitlist": "Y",
    "section_info": {
        "class_details": {
            "institution": "UPITT",
            "subject": "CS",
            "catalog_nbr": "0007",
            "status": "Open",
            "class_number": 27815,
            "component": "REC",
            "course_offer_nbr": 1,
            "session": "Academic Term",
            "session_code": "AT",
            "class_section": "1000",
            "section_descr": "CS 0007 - 1000",
            "units": "0 units",
            "acad_career": "UGRD",
            "acad_career_descr": "",
            "course_id": "105611",
            "course_title": "INTRODUCTION TO COMPUTER PROGRAMMING",
            "course_status": "A",
            "instruction_mode": "",
            "grading_basis": "",
            "campus": "Pittsburgh Campus",
            "campus_code": "PIT",
            "location": "Pittsburgh Campus",
            "topic": "",
            "class_components": '<table class="PSTEXT"><tr><td>Lecture Required, Recitation Required</td></tr></table>',
        },
        "meetings": [
            {
                "meets": "Fr 10:00am - 10:50am",
                "days": "Fr",
                "meeting_time_start": "10:00AM",
                "meeting_time_end": "10:50AM",
                "bldg_cd": "SENSQ",
                "meeting_topic": "TBA",
                "instructors": [{"name": "Robert Fishel", "email": "rmf105@pitt.edu"}],
                "start_date": "08/29/2022",
                "end_date": "12/09/2022",
                "topic": "TBA",
                "show_topic": False,
                "date_range": "08/29/2022 - 12/09/2022",
            }
        ],
        "enrollment_information": {
            "add_consent": "",
            "drop_consent": "",
            "enroll_requirements": "",
            "requirement_desig": "",
            "class_attributes": "DSAS Algebra General Ed. Requirement \rDSAS Quant.-Formal Reason General Ed. Requirement \rAsian Studies",
        },
        "class_availability": {
            "class_capacity": "28",
            "enrollment_total": "24",
            "enrollment_available": 4,
            "wait_list_capacity": "50",
            "wait_list_total": "7",
        },
        "reserve_caps": [],
        "is_combined": False,
        "notes": {"class_notes": "", "subject_notes": ""},
        "catalog_descr": {
            "crse_catalog_description": "This is a first course in computer science programming. It is recommended for those students intending to major in computer science who do not have the required background for cs 0401. It may also be of interest to students majoring in one of the social sciences or humanities. The focus of the course is on problem analysis and the development of algorithms and computer programs in a modern high-level language."
        },
        "materials": {
            "txb_none": "N",
            "txb_status": "P",
            "txb_special_instructions": "",
            "textbooks_message": "Textbooks to be determined",
        },
        "valid_to_enroll": "T",
    },
    "class_enroll_info": {"last_enrl_dt_passed": False, "is_related": True},
    "additionalLinks": [],
    "cfg": {
        "is_related": False,
        "show_crse_id": False,
        "show_crse_offer_nbr": False,
        "show_campus": True,
        "show_location": True,
        "show_consent_to_add": True,
        "show_consent_to_drop": True,
        "show_enroll_req": True,
        "show_req_desig": True,
        "show_class_attributes": True,
        "show_class_availability": True,
        "show_combined": True,
        "show_class_notes": True,
        "show_catalog_descr": True,
        "show_textbook_info": True,
        "show_common_attributes": False,
        "can_add_to_planner": False,
        "show_enroll": False,
        "can_add_to_cart": False,
        "can_enroll_class": False,
        "can_validate_class": False,
        "can_edit_class": False,
        "can_delete_class": False,
        "show_friend_suggest": False,
        "show_bookstore": False,
        "show_share": False,
        "show_wait_list": True,
        "show_instruction_mode": False,
        "show_topic": False,
        "show_add_to_wish_list": False,
        "wish_list_enabled": False,
        "show_actions": True,
    },
    "messages": {
        "shareLink": "Copy link to share the class with friends.",
        "shareSocial": "Or share on social media networks.",
        "reserveInfo": "Seats in this class have been reserved for students for the specified programs, majors or groups listed below. Reserved seats are subject to change without notice.",
        "noMeetingInfo": "No meeting info found",
    },
}

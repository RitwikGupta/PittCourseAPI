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
import responses
from pittapi import people

RAMIREZ_TEST_DATA = """
        <div id="searchResults">
            <section class="row scale-in-center">
                <div class="col single-col">
                    <div class="person-header">
                        <div>
                            <span class="title">
                                        Ramirez, John C<a class="v-card" href="/VCard/Index/7428" target="_blank" title="v-card"><i class="fa fa-address-card" aria-hidden="true"></i></a>
                                    </span>
                        </div>
                    </div>
                    <div class="section-group more-info">
                        <span class="row-label">Employee Information</span><span>
                                        Faculty, SCI-Computer Science                            </span>
                    </div>
                    <div>
                        <span class="row-label section-group">Email</span><span><a href="mailto:ramirez@cs.pitt.edu">ramirez@cs.pitt.edu</a></span>
                    </div>
                    <div><span class="row-label">Office Phone</span><span>(412) 624-8441</span></div>
                    <div class="more-info"><span class="row-label">Office Mailing Address</span><span>6125 Sennott Square</span>
                    </div>
                    <div class="more-info-link"><a>Show More</a></div>
                </div>
            </section>
            <script>
                if ('1' == 1) {
                        $("#resultsInfo").text('1 result found');
                    } else {
                        $("#resultsInfo").text('1 results found');
                    }
                    $(".more-info-link a").click(function () {
                        if ($(this).text() == "Show More") {
                        // $(this).parent().parent().children().removeClass('more-info-hide');
                            $(this).parent().parent().children('.more-info').slideDown('fast');
                            $(this).text('Hide More');
                        } else {
                            $(this).parent().parent().children('.more-info').slideUp('fast');
                            $(this).text('Show More')
                        }
                    });
            </script>
        </div>
        <script>
        </script>
    """

TOO_MANY_TEST_DATA = """
        <div id="searchResults">
            <div class="alert-danger content-alert">
                Too many people matched your criteria. Please try searching by username, phone, email, or by enclosing your
                search in quotation marks.
            </div>
            <script>
                $("#resultsInfo").text('');
            </script>
        </div>
        <script>
        </script>
    """

NONE_FOUND_TEST_DATA = """
        <div id="searchResults">
            <script>
                if ('0' == 1) {
                        $("#resultsInfo").text('0 result found');
                    } else {
                        $("#resultsInfo").text('0 results found');
                    }
                    $(".more-info-link a").click(function () {
                        if ($(this).text() == "Show More") {
                        // $(this).parent().parent().children().removeClass('more-info-hide');
                            $(this).parent().parent().children('.more-info').slideDown('fast');
                            $(this).text('Hide More');
                        } else {
                            $(this).parent().parent().children('.more-info').slideUp('fast');
                            $(this).text('Show More')
                        }
                    });
            </script>
        </div>
        <script>
        </script>
    """


class PeopleTest(unittest.TestCase):
    @responses.activate
    def test_people_get_person(self):
        responses.add(
            responses.POST, people.PEOPLE_SEARCH_URL, body=RAMIREZ_TEST_DATA, status=200
        )
        ans = people.get_person("John C Ramirez")
        self.assertIsInstance(ans, list)
        self.assertTrue(ans[0]["name"] == "Ramirez, John C")
        self.assertTrue(ans[0]["office_phone"] == "(412) 624-8441")

    @responses.activate
    def test_people_get_person_too_many(self):
        responses.add(
            responses.POST,
            people.PEOPLE_SEARCH_URL,
            body=TOO_MANY_TEST_DATA,
            status=200,
        )
        ans = people.get_person("Smith")
        self.assertIsInstance(ans, list)
        self.assertEqual(ans, [{"ERROR": "Too many people matched your criteria."}])

    @responses.activate
    def test_people_get_person_none(self):
        responses.add(
            responses.POST,
            people.PEOPLE_SEARCH_URL,
            body=NONE_FOUND_TEST_DATA,
            status=200,
        )
        ans = people.get_person("Lebron Iverson James Jordan Kobe")
        self.assertIsInstance(ans, list)
        self.assertEqual(ans, [{"ERROR": "No one found."}])

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

from bs4 import BeautifulSoup
import requests


GYM_URL = "https://connect2concepts.com/connect2/?type=bar&key=17c2cbcb-ec92-4178-a5f5-c4860330aea0"


def fetch_gym_info() -> dict:
    """Fetches dictionary of Live Facility Counts of all gyms"""
    gym_dict = {}
    # Was getting a Mod Security Error
    # Fix: https://stackoverflow.com/questions/61968521/python-web-scraping-request-errormod-security
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
    }

    page = requests.get(GYM_URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    gym_info_list = soup.find_all("div", class_="barChart")

    # Iterate through list and add to dictionary
    for gym in gym_info_list:
        text = gym.get_text("|", strip=True)
        info = text.split("|")
        gym_dict[info[0]] = info[2][12:]
    return gym_dict


def get_baierl_rec_count():
    info = fetch_gym_info()
    return info["Baierl Rec Center"]


def get_bellfield_fitness_count():
    info = fetch_gym_info()
    return info["Bellefield Hall: Fitness Center & Weight Room"]


def get_bellfield_court_count():
    info = fetch_gym_info()
    return info["Bellefield Hall: Court & Dance Studio"]


def get_trees_fitness_count():
    info = fetch_gym_info()
    return info["Trees Hall: Fitness Center"]


def get_trees_court_count():
    info = fetch_gym_info()
    return info["Trees Hall: Courts"]


def get_trees_raquetball_court_count():
    info = fetch_gym_info()
    return info["Trees Hall: Racquetball Courts & Multipurpose Room"]


def get_willaim_pitt_fittness_count():
    info = fetch_gym_info()
    return info["William Pitt Union"]


def get_sports_dome_count():
    info = fetch_gym_info()
    return info["Pitt Sports Dome"]

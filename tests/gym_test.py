import unittest
import responses
from pittapi import gym
from tests.mocks.gym_mocks import mock_gym_html


class GymTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    @responses.activate
    def test_fetch_gym_info(self):

        responses.add(responses.GET, gym.GYM_URL, body=mock_gym_html, status=200)

        gym_info = gym.get_all_gyms_info()
        expected_info = [
            gym.Gym(name="Baierl Rec Center", date="07/09/2024 09:05 AM", count=100, percentage=50),
            gym.Gym(name="Bellefield Hall: Fitness Center & Weight Room", date="07/09/2024 09:05 AM", count=50, percentage=0),
            gym.Gym(name="Bellefield Hall: Court & Dance Studio", date=None, count=None, percentage=None),
            gym.Gym(name="Trees Hall: Fitness Center", date="07/09/2024 09:05 AM", count=70, percentage=58),
            gym.Gym(name="Trees Hall: Courts", date="07/09/2024 09:05 AM", count=20, percentage=33),
            gym.Gym(
                name="Trees Hall: Racquetball Courts & Multipurpose Room",
                date="07/09/2024 09:05 AM",
                count=10,
                percentage=25,
            ),
            gym.Gym(name="William Pitt Union", date="07/09/2024 09:05 AM", count=25, percentage=25),
            gym.Gym(name="Pitt Sports Dome", date="07/09/2024 09:05 AM", count=15, percentage=20),
        ]

        self.assertEqual(gym_info, expected_info)

    @responses.activate
    def test_get_gym_info(self):
        responses.add(responses.GET, gym.GYM_URL, body=mock_gym_html, status=200)

        gym_info = gym.get_gym_info("Baierl Rec Center")
        expected_info = gym.Gym(name="Baierl Rec Center", date="07/09/2024 09:05 AM", count=100, percentage=50)
        self.assertEqual(gym_info, expected_info)

    @responses.activate
    def test_invalid_gym_name(self):
        responses.add(responses.GET, gym.GYM_URL, body=mock_gym_html, status=200)

        gym_info = gym.get_gym_info("Invalid Gym Name")
        self.assertIsNone(gym_info)

    @responses.activate
    def test_valid_gym_name_not_all_info(self):
        responses.add(responses.GET, gym.GYM_URL, body=mock_gym_html, status=200)

        gym_info = gym.get_gym_info("Bellefield Hall: Court & Dance Studio")
        self.assertIsNone(gym_info)

    @responses.activate
    def test_percentage_value_error(self):
        responses.add(responses.GET, gym.GYM_URL, body=mock_gym_html, status=200)

        gym_info = gym.get_gym_info("Bellefield Hall: Fitness Center & Weight Roomo")
        self.assertIsNone(gym_info)

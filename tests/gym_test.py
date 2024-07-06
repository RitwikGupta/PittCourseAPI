import unittest
import responses
from pittapi import gym

GYM_URL = "https://connect2concepts.com/connect2/?type=bar&key=17c2cbcb-ec92-4178-a5f5-c4860330aea0"


class GymTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    @responses.activate
    def test_fetch_gym_info(self):
        # Mock the HTML response
        mock_html = """
        <div class="barChart">Baierl Rec Center|Current: 100|Capacity: 200</div>
        <div class="barChart">Bellefield Hall: Fitness Center & Weight Room|Current: 50|Capacity: 150</div>
        <div class="barChart">Bellefield Hall: Court & Dance Studio|Current: 30|Capacity: 80</div>
        <div class="barChart">Trees Hall: Fitness Center|Current: 70|Capacity: 120</div>
        <div class="barChart">Trees Hall: Courts|Current: 20|Capacity: 60</div>
        <div class="barChart">Trees Hall: Racquetball Courts & Multipurpose Room|Current: 10|Capacity: 40</div>
        <div class="barChart">William Pitt Union|Current: 25|Capacity: 100</div>
        <div class="barChart">Pitt Sports Dome|Current: 15|Capacity: 75</div>
        """

        responses.add(responses.GET, GYM_URL, body=mock_html, status=200)

        gym_info = gym.fetch_gym_info()
        self.assertEqual(gym_info["Baierl Rec Center"], "200")
        self.assertEqual(gym_info["Bellefield Hall: Fitness Center & Weight Room"], "150")
        self.assertEqual(gym_info["Bellefield Hall: Court & Dance Studio"], "80")
        self.assertEqual(gym_info["Trees Hall: Fitness Center"], "120")
        self.assertEqual(gym_info["Trees Hall: Courts"], "60")
        self.assertEqual(gym_info["Trees Hall: Racquetball Courts & Multipurpose Room"], "40")
        self.assertEqual(gym_info["William Pitt Union"], "100")
        self.assertEqual(gym_info["Pitt Sports Dome"], "75")

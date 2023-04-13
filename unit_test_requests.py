import logging
import unittest
from random import randrange
import requests
from constants import ARRIVAL, DEPARTURE, SUCCESS, FLIGHT_ID
from successful_flights import SuccessfulFlights
"""
For the first three test in order to run - run server_handler.py
for the last tow - flask_server.py
"""


class MyTestCase(unittest.TestCase):
    logging.basicConfig(level=logging.INFO)
    new_db = SuccessfulFlights()

    def test_get_info(self):
        """
        test get info
        :return:
        """
        flight_id = "TEST"
        flight_value = ["TEST", "00:00", "00:00"]
        url = f"http://localhost:8080/{flight_id}"
        res = requests.get(url=url)
        info = [x.strip('"').strip() for x in res.text.strip("][").split(", ")]
        self.assertEqual(flight_value, info)

    def test_update_a_flight_text(self):
        """
        test update flight with text
        :return:
        """
        flight_id = "CHANGE"
        time_hour = "10"
        time_min = "00"
        url = "http://localhost:8080/"
        payload = f"{flight_id}_{DEPARTURE}_{time_hour}_{time_min}".encode()
        headers = {"Content-type": "text/html"}

        res = requests.post(url, data=payload, headers=headers)
        # get the value and see if its the same as the values given
        url = f"http://localhost:8080/{flight_id}"
        res = requests.get(url=url)
        info = [x.strip('"').strip() for x in res.text.strip("][").split(", ")]
        flight_value = ["CHANGE", "00:00", "10:00"]

        self.assertEqual(flight_value, info)

    def test_update_a_flight_json(self):
        """

        :return:
        """
        flight_id = "CHANGE"
        url = "http://localhost:8080/"
        flight_value = ["CHANGE", "00:00", "11:00"]
        headers = {"Content-type": "application/json"}
        post_request = {
            FLIGHT_ID: flight_id,
            ARRIVAL: "00:00",
            DEPARTURE: "11:00",
        }
        res = requests.post(url, json=post_request, headers=headers)

        url = f"http://localhost:8080/{flight_id}"
        res = requests.get(url=url)
        info = [x.strip('"').strip() for x in res.text.strip("][").split(", ")]
        self.assertEqual(flight_value, info)

    def test_get_info_flask(self, port=8000):
        """
        get info using the flask version
        :param port:
        :return:
        """
        flight_id = "TEST"
        flight_value = {
            ARRIVAL: "00:00",
            DEPARTURE: "00:00",
            FLIGHT_ID: "TEST",
            # SUCCESS: "’’",
        }

        url = f"http://localhost:{port}/flights/{flight_id}"
        res = requests.get(url=url).json()

        self.assertEqual(flight_value[ARRIVAL], res[1])
        self.assertEqual(flight_value[DEPARTURE], res[2])

    def test_update_flight_flask(self, port=8000):
        """
        test update using the flask version
        :param port:
        :return:
        """
        flight_id = "CHANGE"
        url = f"http://localhost:{port}/flights/{flight_id}"
        rnd_time = str(randrange(24))
        arrival = "00:00"
        departure = f"{rnd_time}:00"
        post_request = {ARRIVAL: arrival, DEPARTURE: departure}
        res = requests.post(url=url, data=post_request)

        info = self.new_db.get_info(flight_id=flight_id)
        self.assertEqual(info[2], departure)


if __name__ == "__main__":
    unittest.main()

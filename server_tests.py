import unittest  # unit tests for the server
from server import *
import json


class ServerTests(unittest.TestCase):
    """Tests for the ``server`` functions"""

    def test_test(self):
        self.assertEqual("The server is working.", test())

    def test_get_id(self):
        with app.test_request_context('/id', method='GET'):
            response1 = app.dispatch_request()
            print(response1.data)
            response2 = app.dispatch_request()
            self.assertNotEqual(response1.data, response2.data)

    def test_post_status(self):
        with app.test_request_context('/robot_status/5', method='POST',
                                      json={'id': 5, 'x': 1, "y": 2}):
            response = app.dispatch_request()
            data = json.loads(response.data)
            self.assertIn('GMT', data['update_time'])

    def test(self):
        with self.assertRaises(ValueError):
            raise ValueError("Error")


if __name__ == '__main__':
    unittest.main()

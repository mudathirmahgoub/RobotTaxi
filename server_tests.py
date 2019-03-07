import unittest  # unit tests for the server
from server import *
from werkzeug.exceptions import *
import json


class ServerTests(unittest.TestCase):
    """Tests for the ``server`` functions"""

    def setUp(self):
        app.robots_dictionary = {
            1: RobotState(robot_id=1, x=1, y=1, angle_z_degrees=0),
            2: RobotState(robot_id=2, x=2, y=1, angle_z_degrees=0)
        }
        app.unique_id = len(app.robots_dictionary)

    def test_test(self):
        self.assertEqual("The server is working.", test())

    def test_get_id(self):
        with app.test_request_context('/id', method='GET'):
            response1 = app.dispatch_request()
            print(response1.data)
            response2 = app.dispatch_request()
            self.assertNotEqual(response1.data, response2.data)

    def test_post_status(self):
        robot_id = 1
        with app.test_request_context('/robot_status/{0}'.format(robot_id),
                                      method='POST',
                                      json={'id': robot_id, 'x': 5, "y": 5}):
                response = app.dispatch_request()
                data = json.loads(response.data)
                self.assertIn('GMT', data['update_time'])

    def test(self):
        non_existent_id = 100
        with self.assertRaises(NotFound), app.test_request_context(
                '/robot_status/{0}'.format(non_existent_id),
                method='POST', json={'id': non_existent_id, 'x': 5, "y": 5}):
            app.dispatch_request()


if __name__ == '__main__':
    unittest.main()

import unittest  # unit tests for the server
from server import *


class ServerTests(unittest.TestCase):
    """Tests for the ``server`` functions"""

    def test_test(self):
        self.assertEqual("The server is working.", test())

    def test_get_id(self):
        with app.app_context():
            response1 = get_id()
            print(response1.data)
            response2 = get_id()
            self.assertNotEqual(response1.data, response2.data)

    def test(self):
        with self.assertRaises(ValueError):
            raise ValueError("Error")


if __name__ == '__main__':
    unittest.main()

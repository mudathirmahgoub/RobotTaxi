from shared_client import *
import random


class MockClient(RobotClient):
    def __init__(self):
        x = start_row * cell_length
        y = start_column * cell_length
        angle_z_degrees = 0  # facing down
        RobotClient.__init__(self, 'mock', x, y, angle_z_degrees)

    def move_randomly(self):
        self.x = random.randint(1, 450)
        self.y = random.randint(1, 450)


mock_client = MockClient()
loop(mock_client)

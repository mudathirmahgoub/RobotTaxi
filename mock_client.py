from shared_client import *


class MockClient(RobotClient):
    def __init__(self):
        x = start_row * cell_length
        y = start_column * cell_length
        rotation = 0  # facing down
        RobotClient.__init__(self, 'mock', x, y, rotation)

    def move_randomly(self):
        random_neighbor = RobotClient.get_random_neighbor(self)
        if self.rotation == 0:
            self.x = random_neighbor['row'] * cell_length + cell_length / 5
            self.y = random_neighbor['column'] * cell_length + cell_length / 5
        if self.rotation == 180:
            self.x = random_neighbor['row'] * cell_length + cell_length / 5
            self.y = random_neighbor['column'] * cell_length + 2.5 * cell_length / 5
        if self.rotation == 90:
            self.x = random_neighbor['row'] * cell_length + 2.5 * cell_length / 5
            self.y = random_neighbor['column'] * cell_length + cell_length / 5
        if self.rotation == -90:
            self.x = random_neighbor['row'] * cell_length + cell_length / 5
            self.y = random_neighbor['column'] * cell_length + cell_length / 5


mock_client = MockClient()
loop(mock_client)

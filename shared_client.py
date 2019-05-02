from abc import abstractmethod
from shared import *
import time
import requests
import random

# global variables
api_url = 'http://192.168.0.12:7000/{0}'
map_response = requests.get(api_url.format('map'))
world_map = map_response.json()
cell_length: int = world_map['cellLengthMillimeters']
refresh_rate_milliseconds: int = world_map['refreshRateMilliseconds']
start_row: int = world_map['startRow']
start_column: int = world_map['startColumn']
thresholdMillimeters = world_map['thresholdMillimeters']


def get_cell(row, column):
    cells = [c for c in world_map['cells'] if c['row'] == row and c['column'] == column]
    if len(cells) > 0:
        return cells[0]
    return None


def get_neighbors(cell):
    row, column = cell['row'], cell['column']
    # get the 4 neighbors
    neighbors = [get_cell(row - 1, column),  # top cell
                 get_cell(row, column - 1),  # left cell
                 get_cell(row + 1, column),  # bottom cell
                 get_cell(row, column + 1),  # right cell
                 ]
    # exclude none cells
    neighbors = [c for c in neighbors if c]
    return neighbors


def get_road_neighbors(cell):
    neighbors = get_neighbors(cell)
    neighbors = [c for c in neighbors if c['type'] == 'road']
    return neighbors


class RobotClient:
    def __init__(self, robot_type, x, y, rotation):
        id_response = requests.get(api_url.format('id'))
        self.robot_id = id_response.json()['id']
        self.robot_type = robot_type
        self.x, self.y, self.rotation = x, y, rotation
        self.previous_x, self.previous_y, self.previous_rotation = x, y, rotation  # for transition

    def post_status(self):
        robot_state = RobotState(self.robot_id, self.robot_type, self.x, self.y, self.rotation)
        # print(robot_state.__dict__)
        json_data = RobotEncoder().encode(robot_state)
        requests.post(api_url.format('robot_status/{0}').format(self.robot_id), data=json_data,
                      headers={'Content-type': 'application/json'})

    def get_cell(self):
        # print(self.__dict__)
        row, column = self.x // cell_length, self.y // cell_length
        return get_cell(row, column)

    def get_previous_cell(self):
        row, column = self.previous_x // cell_length, self.previous_y // cell_length
        return get_cell(row, column)

    def get_random_neighbor(self):
        cell = RobotClient.get_cell(self)
        neighbors = get_road_neighbors(cell)
        # exclude backward cells
        current_rotation = self.rotation
        # down
        if current_rotation == 0:
            neighbors = [c for c in neighbors if c['row'] != cell['row'] - 1]
        # up
        if current_rotation == 180:
            neighbors = [c for c in neighbors if c['row'] != cell['row'] + 1]
        # left
        if current_rotation == -90:
            neighbors = [c for c in neighbors if c['column'] != cell['column'] + 1]
        # right
        if current_rotation == 90:
            neighbors = [c for c in neighbors if c['column'] != cell['column'] - 1]

        random_neighbor = neighbors[random.randint(0, len(neighbors) - 1)]
        # determine the direction
        # down
        if random_neighbor['row'] - cell['row'] > 0:
            self.rotation = 0
        # up
        if random_neighbor['row'] - cell['row'] < 0:
            self.rotation = 180
        # right
        if random_neighbor['column'] - cell['column'] > 0:
            self.rotation = 90
        # left
        if random_neighbor['column'] - cell['column'] < 0:
            self.rotation = -90
        return random_neighbor

    def get_random_destination(self):
        random_neighbor = RobotClient.get_random_neighbor(self)
        print('Destination cell: {0}'.format(random_neighbor))
        return self.get_cell_coordinates(random_neighbor)

    def get_cell_coordinates(self, cell):
        # initialization
        x, y = self.x, self.y
        # down down
        if self.previous_rotation == 0 and self.rotation == 0:
            x = cell['row'] * cell_length + 2.5 * cell_length / 5

        # down left
        if self.previous_rotation == 0 and self.rotation == 90:
            x = cell['row'] * cell_length + 4 * cell_length / 5
            y = cell['column'] * cell_length + 2.5 * cell_length / 5

        # left left
        if self.previous_rotation == 90 and self.rotation == 90:
            y = cell['column'] * cell_length + 2.5 * cell_length / 5

        # left up
        if self.previous_rotation == 90 and self.rotation == 180:
            x = cell['row'] * cell_length + 4 * cell_length / 5
            y = cell['column'] * cell_length + 4 * cell_length / 5

        # up up
        if self.previous_rotation == 180 and self.rotation == 180:
            x = cell['row'] * cell_length + 4 * cell_length / 5
        # up right
        if self.previous_rotation == 180 and self.rotation == -90:
            x = cell['row'] * cell_length + 2.5 * cell_length / 5
            y = cell['column'] * cell_length + 4 * cell_length / 5

        # right right
        if self.previous_rotation == -90 and self.rotation == -90:
            y = cell['column'] * cell_length + 4 * cell_length / 5

        # right down
        if self.previous_rotation == -90 and self.rotation == 0:
            x = cell['row'] * cell_length + 2.5 * cell_length / 5
            y = cell['column'] * cell_length + 2.5 * cell_length / 5

        return x, y

    @abstractmethod
    def move_randomly(self):
        pass


def loop(robot_client: RobotClient):
    while True:
        # for now, move randomly. Later we can follow a plan for movement
        robot_client.move_randomly()
        # update the robot status in the server
        robot_client.post_status()
        time.sleep(refresh_rate_milliseconds / 1000)  # convert to seconds

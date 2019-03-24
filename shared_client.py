from abc import abstractmethod
from shared import *
import time
import requests

# global variables
api_url = 'http://192.168.0.12:7000/{0}'
map_response = requests.get(api_url.format('map'))
world_map = map_response.json()
cell_length = world_map['cellLengthMillimeters']
start_row, start_column = world_map['startRow'], world_map['startColumn']


def get_cell(row, column):
    cells = [c for c in world_map['cells'] if c['row'] == row and c['column'] == column]
    if len(cells) > 0:
        return cells[0]
    return None


def get_neighbors(cell):
    row, column = cell['row'], cell['column']
    # get the 8 neighbors
    neighbors = [get_cell(row - 1, column - 1), get_cell(row - 1, column), get_cell(row - 1, column + 1),
                 get_cell(row, column - 1), get_cell(row, column + 1), get_cell(row + 1, column - 1),
                 get_cell(row + 1, column), get_cell(row + 1, column + 1)]
    # exclude none cells
    neighbors = [c for c in neighbors if c]
    return neighbors


def get_road_neighbors(cell):
    neighbors = get_neighbors(cell)
    neighbors = [c for c in neighbors if c['type'] == 'road']
    return neighbors


class RobotClient:
    def __init__(self, robot_type, x, y, angle_z_degrees):
        id_response = requests.get(api_url.format('id'))
        self.robot_id = id_response.json()['id']
        self.robot_type = robot_type
        self.x = x
        self.y = y
        self.angle_z_degrees = angle_z_degrees

    def post_status(self):
        robot_state = RobotState(self.robot_id, self.robot_type, self.x, self.y, self.angle_z_degrees)
        print(robot_state.__dict__)
        json_data = RobotEncoder().encode(robot_state)
        requests.post(api_url.format('robot_status/{0}').format(self.robot_id), data=json_data,
                      headers={'Content-type': 'application/json'})

    def get_cell(self):
        print(self.__dict__)
        row, column = self.x // cell_length, self.y // cell_length
        return get_cell(row, column)

    @abstractmethod
    def move_randomly(self):
        pass


def loop(robot_client: RobotClient):
    while True:
        # for now, move randomly. Later we can follow a plan for movement
        robot_client.move_randomly()
        # update the robot status in the server
        robot_client.post_status()
        time.sleep(.1)

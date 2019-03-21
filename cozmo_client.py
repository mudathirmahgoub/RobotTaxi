from shared import *
import cozmo
from cozmo.util import *
import time
import requests
import random

api_url = 'http://192.168.0.12:7000/{0}'

id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']
robot_type = 'cozmo'

map_response = requests.get(api_url.format('map'))
world_map = map_response.json()
cell_length = world_map['cellLengthMillimeters']
start_row, start_column = world_map['startRow'], world_map['startColumn']


def get_map_cell(x, y):
    row = (x + start_row * cell_length) // cell_length
    column = (y + start_column * cell_length) // cell_length
    cell = list(filter(lambda c: c['row'] == row and c['column'] == column, world_map['cells']))
    return cell


current_cell = get_map_cell(500, 500)


def post_status(x, y, angle_z_degrees=0):
    robot_state = RobotState(robot_id, robot_type, x, y, angle_z_degrees)
    json_data = RobotEncoder().encode(robot_state)
    requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                  headers={'Content-type': 'application/json'})


def cozmo_program(robot: cozmo.robot.Robot):
    map_x, map_y = 0, 0
    robot.drive_straight(distance=distance_inches(20), speed=speed_mmps(50), should_play_anim=False)
    while True:
        pose = robot.pose
        x, y = pose.position.x, pose.position.y
        print(pose)
        post_status(y, x)
        time.sleep(.1)


cozmo.run_program(cozmo_program, use_viewer=True)

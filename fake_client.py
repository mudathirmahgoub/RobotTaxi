from shared import *
import time
import requests
import random

api_url = 'http://192.168.0.12:7000/{0}'

id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']
robot_type = 'cozmo'


def post_status():
    x, y, angle_z_degrees = random.randint(1, 450), random.randint(1, 450), 0
    robot_state = RobotState(robot_id, robot_type, x, y, angle_z_degrees)
    json_data = RobotEncoder().encode(robot_state)
    print(json_data)
    response = requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                             headers={'Content-type': 'application/json'})
    print(response.json())


while True:
    post_status()
    time.sleep(.1)

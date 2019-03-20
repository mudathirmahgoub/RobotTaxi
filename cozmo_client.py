from shared import *
import cozmo
import time
import requests
import random

api_url = 'http://192.168.0.12:7000/{0}'

id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']
robot_type = 'cozmo'


def post_status():
    x, y, angle_z_degrees = random.randint(1,100), random.randint(1,100), 0
    robot_state = RobotState(robot_id, robot_type, x, y, angle_z_degrees)
    json_data = json.dumps(robot_state, cls=RobotEncoder)
    response = requests.post(api_url.format('robot_status/{0}').format(robot_id), json=json_data)
    print(response.json())


def cozmo_program(robot: cozmo.robot.Robot):
    while True:
        pose = robot.pose
        print(pose)
        post_status()
        time.sleep(.1)


cozmo.run_program(cozmo_program, use_viewer=True)

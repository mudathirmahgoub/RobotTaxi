from shared import *
import cozmo
import time
import requests

api_url = 'http://192.168.0.12:7000/{0}'

response = requests.get(api_url.format('id'))
robot_id = response.json()['id']

#
# def cozmo_program(robot: cozmo.robot.Robot):
#     while True:
#         time.sleep(.01)
#
#
# cozmo.run_program(cozmo_program)

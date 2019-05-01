from threading import *
from shared_client import *


left_speed, right_speed = 50, 50
big_turn = 50
small_turn = 5
turn = 20

id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']

x, y, rotation = 0, 0, 0


def post_status():
    global x, y, rotation
    print(x)
    robot_state = RobotState(robot_id, 'cozmo', x, y, rotation)
    json_data = RobotEncoder().encode(robot_state)
    print(json_data)
    requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                  headers={'Content-type': 'application/json'})
    Timer(0.1, post_status).start()


def post_image(x, y):
    row, column = x // cell_length, y // cell_length
    return 'straight'


wheels_speeds = {
    'straight': (left_speed, right_speed),
    'cross': (left_speed, right_speed),
    'corner-left': (turn + small_turn, right_speed),
    'corner-right': (left_speed, turn),
    'turn-left': (left_speed - small_turn, right_speed + small_turn),
    'turn-right': (left_speed + small_turn, right_speed - small_turn),
    'stop': (0, 0),
    'turn-left-left': (turn, right_speed),
    'turn-right-right': (left_speed, turn),
}


def program():
    global x, y, rotation
    Timer(0.1, post_status).start()
    while True:
        image_class = post_image(x, y)
        (left, right) = wheels_speeds.get(image_class, (0, 0))
        x += 20
        time.sleep(refresh_rate_milliseconds / 1000)  # convert to seconds


if __name__ == '__main__':
    program()

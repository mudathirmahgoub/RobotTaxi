from threading import *
from shared_client import *
import sys

robot_type = 'cozmo'
id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']
trip = None
x, y, rotation = 0, 0, 0
previous_row, previous_column = start_row, start_column
target_row, target_column = start_row + 1, start_column
speed = 20


def get_cell(row, column):
    cells = [c for c in world_map['cells'] if c['row'] == row and c['column'] == column]
    if len(cells) > 0:
        return cells[0]
    return None


def post_status():
    global x, y, rotation
    global x, y, rotation, trip
    if trip:
        row, column = x // cell_length, y // cell_length
        current_row, current_column = row + start_row, column + start_column
        if trip['status'] == 'waiting' and \
                current_row == trip['start']['row'] and current_column == trip['start']['column']:
            trip['status'] = 'started'
        if trip['status'] == 'started' and \
                current_row == trip['end']['row'] and current_column == trip['end']['column']:
            trip['status'] = 'finished'

    robot_state = RobotState(robot_id, robot_type, x, y, rotation, trip)
    print(robot_state.__dict__)
    json_data = RobotEncoder().encode(robot_state)
    response = requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                             headers={'Content-type': 'application/json'})
    trip = response.json()['trip']
    print(trip)
    Timer(0.1, post_status).start()


def post_image():
    global previous_row, previous_column
    global target_row, target_column, x, y, rotation

    print(f'({x}, {y}, {rotation})')

    row, column = x // cell_length, y // cell_length
    current_row, current_column = row + start_row, column + start_column
    if abs(target_row - current_row) > 0 and target_column == current_column:
        y = (target_column - start_column) * cell_length
        if target_row > current_row:
            rotation = 0
            x = x + speed
        else:
            rotation = 180
            x = x - speed

    elif abs(target_column - current_column) > 0 and target_row == current_row:
        x = (target_row - start_row) * cell_length + cell_length / 2
        if target_column > current_column:
            rotation = 90
            y = y + speed
        else:
            rotation = -90
            y = y - speed

    else:
        get_new_target(current_column, current_row)


def get_new_target(current_column, current_row):
    global target_row, target_column, previous_row, previous_column
    cell = get_cell(current_row, current_column)
    print(cell)
    if cell['shape'] == 'straightVertical':
        if current_row > previous_row:
            target_row = current_row + 1
        else:
            target_row = current_row - 1
    if cell['shape'] == 'straightHorizontal':
        if current_column > previous_column:
            target_column = current_column + 1
        else:
            target_column = current_column - 1
    if cell['shape'] == 'curveBottomLeft':
        if current_row > previous_row:
            target_column = current_column + 1
        else:
            pass
    if cell['shape'] == 'curveBottomRight':
        if current_column > previous_column:
            target_row = current_row - 1
        else:
            pass
    if cell['shape'] == 'curveTopRight':
        if current_row < previous_row:
            target_column = current_column - 1
        else:
            pass
    if cell['shape'] == 'curveTopLeft':
        if current_column < previous_column:
            target_row = current_row + 1
        else:
            pass
    if cell['shape'] == 'tRight':
        target_row = current_row + 1
    if cell['shape'] == 'tBottom':
        target_column = current_column - 1
    if cell['shape'] == 'tTop':
        coin = random.randint(0, 1)
        if coin == 1:  # go straight
            target_column = current_column + 1
        else:  # turn left
            target_row = current_row - 1
    if cell['shape'] == 'tLeft':
        coin = random.randint(0, 1)
        if coin == 1:  # go straight
            target_row = current_row - 1
        else:  # turn left
            target_column = current_column - 1

    if cell['shape'] == 'cross':
        coin = random.randint(0, 1)
        if coin == 1:  # turn left
            target_column = current_column - 1
        else:  # go straight
            target_row = current_row - 1
    previous_row, previous_column = current_row, current_column


def program():
    global x, y, rotation
    Timer(0.1, post_status).start()
    while True:
        post_image()
        time.sleep(refresh_rate_milliseconds / 8000)  # convert to seconds


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # specify the robot type either 'cozmo' or 'vector'
        robot_type = sys.argv[1]
    else:
        # default is cozmo
        robot_type = 'cozmo'
    program()

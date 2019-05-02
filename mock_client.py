from threading import *
from shared_client import *
import sys

robot_type = 'cozmo'
id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']
trip: Trip = None
x: int = 0
y: int = 0
rotation: int = 0
previous_row: int = start_row
previous_column: int = start_column
target_row: int = start_row + 1
target_column: int = start_column

speed: int = 20


def post_status():
    global x, y, rotation, trip
    if trip:
        row: int = x // cell_length
        column: int = y // cell_length
        current_row, current_column = row + start_row, column + start_column
        if trip.status == 'waiting' and \
                current_row == trip.start['row'] and current_column == trip.start['column']:
            trip.status = 'started'
        if trip.status == 'started' and \
                current_row == trip.end['row'] and current_column == trip.end['column']:
            trip.status = 'finished'

    if trip:
        robot_state = RobotState(robot_id, robot_type, x, y, rotation, trip=trip)
    else:
        robot_state = RobotState(robot_id, robot_type, x, y, rotation, trip)
    json_data = RobotEncoder().encode(robot_state)
    response = requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                             headers={'Content-type': 'application/json'})
    trip_json = response.json()
    if trip_json['trip']:
        trip = Trip(**trip_json['trip'])
    else:
        trip = None
    Timer(0.1, post_status).start()


def post_image():
    global previous_row, previous_column
    global target_row, target_column, x, y, rotation

    row: int = x // cell_length
    column: int = y // cell_length
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
    elif cell['shape'] == 'straightHorizontal':
        if current_column > previous_column:
            target_column = current_column + 1
        else:
            target_column = current_column - 1
    elif cell['shape'] == 'curveBottomLeft':
        if current_row > previous_row:
            target_column = current_column + 1
        else:
            target_row = current_row - 1
    elif cell['shape'] == 'curveBottomRight':
        if current_column > previous_column:
            target_row = current_row - 1
        else:
            target_column = current_column - 1

    elif cell['shape'] == 'curveTopRight':
        if current_row < previous_row:
            target_column = current_column - 1
        else:
            target_row = current_row + 1
    elif cell['shape'] == 'curveTopLeft':
        if current_column < previous_column:
            target_row = current_row + 1
        else:
            target_column = current_column + 1

    # decision cells
    if trip:
        trip_row, trip_column = get_trip_location(trip)
        # choose the nearest one
        if cell['shape'] == 'tRight':
            if rotation == 0:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 180:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == -90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tTop':
            if rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]

            elif rotation == -90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 0:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tLeft':
            if rotation == 0:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 180:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tBottom':
            if rotation == 90:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == -90:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 180:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        if cell['shape'] == 'cross':
            if rotation == 0:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]

            elif rotation == 180:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif rotation == -90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
    else:
        # make a random choice
        binary_choice = random.randint(0, 1)
        if cell['shape'] == 'tRight':
            if rotation == 0 and binary_choice == 0:
                target_row = current_row + 1
            elif rotation == 0 and binary_choice == 1:
                target_column = current_column + 1
            elif rotation == 180 and binary_choice == 0:
                target_row = current_row - 1
            elif rotation == 180 and binary_choice == 1:
                target_column = current_column + 1
            elif rotation == -90 and binary_choice == 0:
                target_row = current_row - 1
            else:
                target_row = current_row + 1
        elif cell['shape'] == 'tTop':
            if rotation == 90 and binary_choice == 0:
                target_row = current_row - 1
            elif rotation == 90 and binary_choice == 1:
                target_column = current_column + 1
            elif rotation == -90 and binary_choice == 0:
                target_row = current_row - 1
            elif rotation == -90 and binary_choice == 1:
                target_column = current_column - 1
            elif rotation == 0 and binary_choice == 0:
                target_column = current_column - 1
            else:
                target_column = current_column + 1
        elif cell['shape'] == 'tLeft':
            if rotation == 0 and binary_choice == 0:
                target_row = current_row + 1
            elif rotation == 0 and binary_choice == 1:
                target_column = current_column - 1
            elif rotation == 180 and binary_choice == 0:
                target_row = current_row - 1
            elif rotation == 180 and binary_choice == 1:
                target_column = current_column - 1
            elif rotation == 90 and binary_choice == 0:
                target_row = current_row - 1
            else:
                target_row = current_row + 1
        elif cell['shape'] == 'tBottom':
            if rotation == 90 and binary_choice == 0:
                target_row = current_row + 1
            elif rotation == 90 and binary_choice == 1:
                target_column = current_column + 1
            elif rotation == -90 and binary_choice == 0:
                target_row = current_row + 1
            elif rotation == -90 and binary_choice == 1:
                target_column = current_column - 1
            elif rotation == 180 and binary_choice == 0:
                target_column = current_column - 1
            else:
                target_column = current_column + 1
        if cell['shape'] == 'cross':
            ternary_choice = random.randint(0, 2)
            if rotation == 0 and ternary_choice == 0:
                target_column = current_column - 1
            elif rotation == 0 and ternary_choice == 1:
                target_row = current_row + 1
            elif rotation == 0 and ternary_choice == 2:
                target_column = current_column + 1
            elif rotation == 180 and ternary_choice == 0:
                target_column = current_column - 1
            elif rotation == 180 and ternary_choice == 1:
                target_row = current_row - 1
            elif rotation == 180 and ternary_choice == 2:
                target_column = current_column + 1
            elif rotation == 90 and ternary_choice == 0:
                target_row = current_row - 1
            elif rotation == 90 and ternary_choice == 1:
                target_column = current_column + 1
            elif rotation == 90 and ternary_choice == 2:
                target_row = current_row + 1
            elif rotation == -90 and ternary_choice == 0:
                target_row = current_row - 1
            elif rotation == -90 and ternary_choice == 1:
                target_column = current_column - 1
            elif rotation == -90 and ternary_choice == 2:
                target_row = current_row + 1
    previous_row, previous_column = current_row, current_column


def program():
    global x, y, rotation
    Timer(0.1, post_status).start()
    while True:
        post_image()
        time.sleep(0.1)  # convert to seconds


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # specify the robot type either 'cozmo' or 'vector'
        robot_type = sys.argv[1]
    else:
        # default is cozmo
        robot_type = 'cozmo'
    program()

import cozmo
from threading import *
from shared_client import *
from io import BytesIO

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

left_speed, right_speed = 50, 50
big_turn = 50
small_turn = 5
turn = 20
image_class = None


def post_status(robot: cozmo.robot.Robot):
    global x, y, rotation, trip
    x, y, rotation = robot.pose.position.x, robot.pose.position.y, robot.pose.rotation.angle_z.degrees
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
    Timer(0.1, post_status, kwargs={'robot': robot}).start()


def post_image(image):
    image_io = BytesIO()
    image.save(image_io, 'JPEG')
    image_io.seek(0)
    files = {'test.jpeg': ('test.jpeg', image_io, 'multipart/form-data')}
    response = requests.post(api_url.format('classify_image/{0}').format(robot_id), files=files)
    return response.json()['image_class']


def get_new_target(current_column, current_row):
    global target_row, target_column, previous_row, previous_column, rotation
    approximations = [(0, 0 - rotation),
                      (180, 180 - rotation),
                      (90, 90 - rotation),
                      (-90, -90 - rotation)]
    approximations.sort(key=lambda r : abs(r[1]))  # sort by rotation difference
    approximate_rotation = approximations[0][0]
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
            if approximate_rotation == 0:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 180:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == -90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tTop':
            if approximate_rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]

            elif approximate_rotation == -90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 0:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tLeft':
            if approximate_rotation == 0:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 180:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        elif cell['shape'] == 'tBottom':
            if approximate_rotation == 90:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == -90:
                directions = [((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 180:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
        if cell['shape'] == 'cross':
            if approximate_rotation == 0:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]

            elif approximate_rotation == 180:
                directions = [((current_row, current_column - 1),
                               distance(current_row, current_column - 1, trip_row, trip_column)),
                              ((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == 90:
                directions = [((current_row - 1, current_column),
                               distance(current_row - 1, current_column, trip_row, trip_column)),
                              ((current_row, current_column + 1),
                               distance(current_row, current_column + 1, trip_row, trip_column)),
                              ((current_row + 1, current_column),
                               distance(current_row + 1, current_column, trip_row, trip_column)),
                              ]
                directions.sort(key=lambda pair: pair[1])  # sort using the distance
                target_row, target_column = directions[0][0]
            elif approximate_rotation == -90:
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
            if approximate_rotation == 0 and binary_choice == 0:
                target_row = current_row + 1
            elif approximate_rotation == 0 and binary_choice == 1:
                target_column = current_column + 1
            elif approximate_rotation == 180 and binary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == 180 and binary_choice == 1:
                target_column = current_column + 1
            elif approximate_rotation == -90 and binary_choice == 0:
                target_row = current_row - 1
            else:
                target_row = current_row + 1
        elif cell['shape'] == 'tTop':
            if approximate_rotation == 90 and binary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == 90 and binary_choice == 1:
                target_column = current_column + 1
            elif approximate_rotation == -90 and binary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == -90 and binary_choice == 1:
                target_column = current_column - 1
            elif approximate_rotation == 0 and binary_choice == 0:
                target_column = current_column - 1
            else:
                target_column = current_column + 1
        elif cell['shape'] == 'tLeft':
            if approximate_rotation == 0 and binary_choice == 0:
                target_row = current_row + 1
            elif approximate_rotation == 0 and binary_choice == 1:
                target_column = current_column - 1
            elif approximate_rotation == 180 and binary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == 180 and binary_choice == 1:
                target_column = current_column - 1
            elif approximate_rotation == 90 and binary_choice == 0:
                target_row = current_row - 1
            else:
                target_row = current_row + 1
        elif cell['shape'] == 'tBottom':
            if approximate_rotation == 90 and binary_choice == 0:
                target_row = current_row + 1
            elif approximate_rotation == 90 and binary_choice == 1:
                target_column = current_column + 1
            elif approximate_rotation == -90 and binary_choice == 0:
                target_row = current_row + 1
            elif approximate_rotation == -90 and binary_choice == 1:
                target_column = current_column - 1
            elif approximate_rotation == 180 and binary_choice == 0:
                target_column = current_column - 1
            else:
                target_column = current_column + 1
        if cell['shape'] == 'cross':
            ternary_choice = random.randint(0, 2)
            if approximate_rotation == 0 and ternary_choice == 0:
                target_column = current_column - 1
            elif approximate_rotation == 0 and ternary_choice == 1:
                target_row = current_row + 1
            elif approximate_rotation == 0 and ternary_choice == 2:
                target_column = current_column + 1
            elif approximate_rotation == 180 and ternary_choice == 0:
                target_column = current_column - 1
            elif approximate_rotation == 180 and ternary_choice == 1:
                target_row = current_row - 1
            elif approximate_rotation == 180 and ternary_choice == 2:
                target_column = current_column + 1
            elif approximate_rotation == 90 and ternary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == 90 and ternary_choice == 1:
                target_column = current_column + 1
            elif approximate_rotation == 90 and ternary_choice == 2:
                target_row = current_row + 1
            elif approximate_rotation == -90 and ternary_choice == 0:
                target_row = current_row - 1
            elif approximate_rotation == -90 and ternary_choice == 1:
                target_column = current_column - 1
            elif approximate_rotation == -90 and ternary_choice == 2:
                target_row = current_row + 1
    previous_row, previous_column = current_row, current_column


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


def cozmo_program(robot: cozmo.robot.Robot):
    global image_class
    # reset lift and head
    robot.move_lift(0)
    robot.move_head(-1.0)
    robot.camera.image_stream_enabled = True
    Timer(0.1, post_status, kwargs={'robot': robot}).start()
    while True:
        robot.world.wait_for(cozmo.world.EvtNewCameraImage)
        image = robot.world.latest_image.raw_image
        image = image.resize((224, 224))
        image_class = post_image(image)
        row: int = x // cell_length
        column: int = y // cell_length
        current_row, current_column = row + start_row, column + start_column
        cell = get_cell(current_row, current_column)
        print(cell)
        (left, right) = wheels_speeds.get(image_class, (0, 0))
        print(f'{image_class}: ({left},{right})')
        robot.drive_wheels(left, right)


cozmo.run_program(cozmo_program, use_viewer=True)

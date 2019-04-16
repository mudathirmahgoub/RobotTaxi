import cozmo
from threading import *
from shared_client import *
from io import BytesIO


left_speed, right_speed = 50, 50
big_turn = 50
small_turn = 5
turn = 20
image_class = None

id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']


def post_status(robot: cozmo.robot.Robot):
    x, y, rotation = robot.pose.position.x, robot.pose.position.y, robot.pose.rotation.angle_z.degrees
    robot_state = RobotState(robot_id, 'cozmo', x, y, rotation)
    json_data = RobotEncoder().encode(robot_state)
    requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                  headers={'Content-type': 'application/json'})
    Timer(0.1, post_status, kwargs={'robot': robot}).start()


def post_image(image):
    image_io = BytesIO()
    image.save(image_io, 'JPEG')
    image_io.seek(0)
    files = {'test.jpeg': ('test.jpeg', image_io, 'multipart/form-data')}
    response = requests.post(api_url.format('classify_image/{0}').format(robot_id), files=files)
    return response.json()['image_class']


wheels_speeds = {
    'straight': (left_speed, right_speed),
    'cross': (left_speed, right_speed),
    'corner-left': (turn + small_turn, right_speed),
    'corner-right': (left_speed, turn),
    'turn-left': (left_speed - small_turn, right_speed + small_turn),
    'turn-right': (left_speed + small_turn, right_speed - small_turn),
    'stop': (0, 0),
    'turn-left-left': (turn, right_speed + turn),
    'turn-right-right': (left_speed + turn, turn),
}


def cozmo_program(robot: cozmo.robot.Robot):
    global image_class
    robot.camera.image_stream_enabled = True
    Timer(0.1, post_status, kwargs={'robot': robot}).start()
    while True:
        robot.world.wait_for(cozmo.world.EvtNewCameraImage)
        image = robot.world.latest_image.raw_image
        image = image.resize((224, 224))
        image_class = post_image(image)
        print(image_class)
        (left, right) = wheels_speeds.get(image_class, (0, 0))
        print(f'({left},{right})')
        robot.drive_wheels(left, right)


cozmo.run_program(cozmo_program, use_viewer=True)

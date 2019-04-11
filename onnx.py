import cozmo
import time
import matlab.engine
from threading import *
from shared_client import *
names = matlab.engine.find_matlab()
print(names)
# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')

left_speed, right_speed = 50, 50
big_turn = 50
small_turn = 20
image_class = None
processing = False

api_url = 'http://192.168.0.12:7000/{0}'
id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']


def post_status(robot: cozmo.robot.Robot):
    x, y = robot.pose.position.x, robot.pose.position.y
    robot_state = RobotState(robot_id, 'cozmo', x, y, 0)
    json_data = RobotEncoder().encode(robot_state)
    requests.post(api_url.format('robot_status/{0}').format(robot_id), data=json_data,
                  headers={'Content-type': 'application/json'})
    Timer(0.1, post_status, kwargs={'robot': robot}).start()


def on_new_camera_image(evt, **kwargs):
    global image_class, processing, take_image
    if not processing:
        processing = True
        image = kwargs['image'].raw_image
        image = image.resize((224, 224))
        image.save(f"data/current_image.jpeg", "JPEG")
        matlab_engine.classify_image(nargout=0)
        image_class = matlab_engine.eval('class')
        print(image_class)
        processing = False


wheels_speeds = {
    'straight': (left_speed, right_speed),
    'corner_left': (small_turn, right_speed),
    'corner_right': (left_speed, small_turn),
    'turn_left': (left_speed - small_turn, right_speed + small_turn / 2),
    'turn_right': (left_speed + small_turn / 2, right_speed - small_turn)
}


def cozmo_program(robot: cozmo.robot.Robot):
    global image_class, processing
    robot.camera.image_stream_enabled = True
    Timer(0.1, post_status, kwargs={'robot': robot}).start()
    # robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    # global_robot.drive_wheels(left_speed, right_speed)
    while True:
        robot.world.wait_for(cozmo.world.EvtNewCameraImage)
        image = robot.world.latest_image.raw_image
        image = image.resize((224, 224))
        image.save(f"data/current_image.jpeg", "JPEG")
        matlab_engine.classify_image(nargout=0)
        image_class = matlab_engine.eval('class')
        print(image_class)
        (left, right) = wheels_speeds.get(image_class, (0, 0))
        print(f'({left},{right})')
        robot.drive_wheels(left, right)


cozmo.run_program(cozmo_program, use_viewer=True)

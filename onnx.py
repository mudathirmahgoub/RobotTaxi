import cozmo
import time
import matlab.engine

names = matlab.engine.find_matlab()
print(names)
# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')

left_speed, right_speed = 100, 100
big_turn = 50
small_turn = 10
image_class = None


def on_new_camera_image(evt, **kwargs):
    global image_class
    image = kwargs['image'].raw_image
    image = image.resize((224, 224))
    image.save(f"data/current_image.jpeg", "JPEG")
    matlab_engine.classify_image(nargout=0)
    image_class = matlab_engine.eval('class')
    print(image_class)


wheels_speeds = {
    'straight': (left_speed, right_speed),
    'corner_left': (left_speed, right_speed + big_turn),
    'corner_right': (left_speed + big_turn, right_speed),
    'turn_left': (left_speed, right_speed + small_turn),
    'turn_right': (left_speed + small_turn, right_speed)
}


def cozmo_program(robot: cozmo.robot.Robot):
    global image_class
    robot.camera.image_stream_enabled = True
    # robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    # global_robot.drive_wheels(left_speed, right_speed)
    while True:
        time.sleep(1)
        robot.world.wait_for(cozmo.world.EvtNewCameraImage)
        image = robot.world.latest_image.raw_image
        image = image.resize((224, 224))
        image.save(f"data/current_image.jpeg", "JPEG")
        matlab_engine.classify_image(nargout=0)
        image_class = matlab_engine.eval('class')
        print(image_class)
        (left, right) = wheels_speeds.get(image_class, (0, 0))
        robot.drive_wheels(left, right_speed)


cozmo.run_program(cozmo_program)

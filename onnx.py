import cozmo
import time
import matlab.engine

names = matlab.engine.find_matlab()
print(names)
# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')
camera_on = True

global_robot: cozmo.robot.Robot = None
left_speed, right_speed = 100, 100
big_turn = 50
small_turn = 10


def on_new_camera_image(evt, **kwargs):
    global camera_on, global_robot
    global left_speed, right_speed, big_turn, small_turn

    print(evt)
    print(kwargs)

    if camera_on:
        image = kwargs['image'].raw_image
        image = image.resize((224, 224))
        image.save(f"data/current_image.jpeg", "JPEG")
        matlab_engine.classify_image(nargout=0)
        image_class = matlab_engine.eval('class')
        print(image_class)
        if image_class == 'straight':
            global_robot.drive_wheels(left_speed, right_speed)
        if image_class == 'corner_left':
            global_robot.drive_wheels(left_speed, right_speed + big_turn)
        if image_class == 'corner_right':
            global_robot.drive_wheels(left_speed + big_turn, right_speed)
        if image_class == 'turn_left':
            global_robot.drive_wheels(left_speed, right_speed + small_turn)
        if image_class == 'turn_right':
            global_robot.drive_wheels(left_speed + small_turn, right_speed)


def cozmo_program(robot: cozmo.robot.Robot):
    global camera_on, global_robot
    global_robot = robot
    global_robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    # global_robot.drive_wheels(left_speed, right_speed)
    while True:
        camera_on = True
        time.sleep(1)
        camera_on = False


cozmo.run_program(cozmo_program, use_viewer=True)

import cozmo
import time
import matlab.engine
names = matlab.engine.find_matlab()
print(names)
# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')
camera_on = True


def on_new_camera_image(evt, **kwargs):
    global camera_on
    if camera_on:
        image = kwargs['image'].raw_image
        image.save(f"data/current_image.jpeg", "JPEG")
        matlab_engine.classify_image(nargout=0)
        image_class = matlab_engine.eval('class')
        print(image_class)


def cozmo_program(robot: cozmo.robot.Robot):
    robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)
    while True:
        camera_on = True
        time.sleep(1)
        camera_on = False


cozmo.run_program(cozmo_program, use_viewer=True)

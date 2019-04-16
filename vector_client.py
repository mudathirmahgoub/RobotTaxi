import anki_vector
from threading import *
from shared_client import *
from io import BytesIO

left_speed, right_speed = 50, 50
big_turn = 50
small_turn = 5
turn = 20
id_response = requests.get(api_url.format('id'))
robot_id = id_response.json()['id']


def post_status(robot: anki_vector.robot.Robot):
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
    'turn-left-left': (turn, right_speed),
    'turn-right-right': (left_speed, turn),
}


def main():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial, enable_camera_feed=True, show_viewer=True) as robot:
        Timer(0.1, post_status, kwargs={'robot': robot}).start()
        latest_image = None
        # change color to black and white
        # https://stackoverflow.com/questions/53231270/how-to-convert-grayscale-image-to-given-color-monchrome-image-in-pil
        matrix = (0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0, 0.2, 0.5, 0.3, 0.0)
        while True:
            image = robot.camera.latest_image
            if image != latest_image:
                time.sleep(refresh_rate_milliseconds / 1000)  # convert to seconds
                print(robot.camera.latest_image_id)
                latest_image = image
                image = image.resize((224, 224))
                image = image.convert('RGB', matrix)
                image_class = post_image(image)
                (left, right) = wheels_speeds.get(image_class, (0, 0))
                print(f'{image_class}: ({left},{right})')
                robot.motors.set_wheel_motors(left, right)


if __name__ == "__main__":
    main()

from shared_client import *
import cozmo
from cozmo.util import *


def get_coordinates(pose: Pose):
    return pose.position.y, pose.position.x


class CozmoClient(RobotClient):
    def __init__(self, robot: cozmo.robot.Robot):
        x = start_row * cell_length
        y = start_column * cell_length
        angle_z_degrees = 0  # facing down
        self.robot = robot
        self.current_action: cozmo.Action = None
        RobotClient.__init__(self, 'cozmo', x, y, angle_z_degrees)

    def move_randomly(self):
        if not self.current_action or self.current_action.is_completed:
            self.current_action = self.robot.drive_straight(distance=distance_mm(cell_length),
                                                            speed=speed_mmps(cell_length), should_play_anim=False)
        pose = self.robot.pose
        self.x, self.y = get_coordinates(pose)


def cozmo_program(robot: cozmo.robot.Robot):
    cozmo_client = CozmoClient(robot)
    loop(cozmo_client)


cozmo.run_program(cozmo_program, use_viewer=True)

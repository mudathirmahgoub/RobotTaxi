from shared_client import *
import cozmo
from cozmo.util import *


def get_map_coordinates(pose: Pose):
    return pose.position.x + start_row * cell_length, \
           pose.position.y + start_column * cell_length + cell_length / 5


def get_robot_coordinates(map_x, map_y):
    return map_x - start_row * cell_length, \
           map_y - start_column * cell_length - cell_length / 5


class CozmoClient(RobotClient):
    def __init__(self, robot: cozmo.robot.Robot):
        x = start_row * cell_length
        y = start_column * cell_length + cell_length / 5
        angle_z_degrees = 0  # facing down
        self.robot = robot
        self.current_action: cozmo.Action = None
        RobotClient.__init__(self, 'cozmo', x, y, angle_z_degrees)

    def move_randomly(self):
        if not self.current_action or self.current_action.is_completed:
            map_x, map_y = RobotClient.get_random_destination(self)
            robot_x, robot_y = get_robot_coordinates(map_x, map_y)
            pose = self.robot.pose
            if abs(pose.position.x - robot_x) > 0:
                self.current_action = self.robot.drive_straight(distance=distance_mm(cell_length),
                                                                speed=speed_mmps(cell_length), should_play_anim=False)
            
        pose = self.robot.pose
        self.x, self.y = get_map_coordinates(pose)


def cozmo_program(robot: cozmo.robot.Robot):
    cozmo_client = CozmoClient(robot)
    loop(cozmo_client)


cozmo.run_program(cozmo_program, use_viewer=False)

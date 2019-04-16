from shared_client import *
import cozmo
from cozmo.util import *
from collections import deque


def get_map_coordinates(pose: Pose):
    return pose.position.x + start_row * cell_length, \
           pose.position.y + start_column * cell_length + cell_length / 5


def get_robot_coordinates(map_x, map_y):
    return map_x - start_row * cell_length, \
           map_y - start_column * cell_length - cell_length / 5


class CozmoClient(RobotClient):
    def __init__(self, robot: cozmo.robot.Robot):
        x, y = get_map_coordinates(Pose(0, 0, 0, angle_z=Angle(degrees=0)))
        angle_z_degrees = 0  # facing down
        self.robot = robot
        self.current_action: cozmo.Action = None
        self.actions_queue = deque()
        RobotClient.__init__(self, 'cozmo', x, y, angle_z_degrees)

    def move_randomly(self):
        if len(self.actions_queue) == 0 \
                and (not self.current_action or self.current_action.is_completed):
            map_x, map_y = RobotClient.get_random_destination(self)
            robot_x, robot_y = get_robot_coordinates(map_x, map_y)
            print('Pos = ({0}, {1})'.format(self.x, self.y))
            print('(robot_x, robot_y) = ({0}, {1})'.format(robot_x, robot_y))
            print('(map_x, map_y) = ({0}, {1})'.format(map_x, map_y))

            # down down
            if self.previous_rotation == 0 and self.rotation == 0:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # down left
            if self.previous_rotation == 0 and self.rotation == 90:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

                function = self.robot.turn_in_place
                arguments = {'angle': Angle(degrees=90)}  # turn left
                self.actions_queue.append((function, arguments))

                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # left left
            if self.previous_rotation == 90 and self.rotation == 90:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # left up
            if self.previous_rotation == 90 and self.rotation == 180:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

                function = self.robot.turn_in_place
                arguments = {'angle': Angle(degrees=90)}  # turn left
                self.actions_queue.append((function, arguments))

                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # up up
            if self.previous_rotation == 180 and self.rotation == 180:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # up right
            if self.previous_rotation == 180 and self.rotation == -90:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

                function = self.robot.turn_in_place
                arguments = {'angle': Angle(degrees=90)}  # turn left
                self.actions_queue.append((function, arguments))

                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # right right
            if self.previous_rotation == -90 and self.rotation == -90:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            # right down
            if self.previous_rotation == -90 and self.rotation == 0:
                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.y - map_y)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

                function = self.robot.turn_in_place
                arguments = {'angle': Angle(degrees=90)}  # turn left
                self.actions_queue.append((function, arguments))

                function = self.robot.drive_straight
                arguments = {
                    'distance': distance_mm(abs(self.x - map_x)),
                    'speed': speed_mmps(cell_length),
                    'should_play_anim': False}
                self.actions_queue.append((function, arguments))

            self.previous_rotation = self.rotation
            self.x, self.y = map_x, map_y
        else:
            if not self.current_action or self.current_action.is_completed:
                (function, arguments) = self.actions_queue.popleft()
                self.current_action = function(**arguments)
            

def cozmo_program(robot: cozmo.robot.Robot):
    cozmo_client = CozmoClient(robot)
    loop(cozmo_client)


cozmo.run_program(cozmo_program, use_viewer=True)

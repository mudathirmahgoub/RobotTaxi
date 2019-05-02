import json
from datetime import *


class Location:
    def __init__(self, row, column):
        """
        :param row: the current row with respect to the map
        :param column: the current column with respect to the map
        """
        self.row, self.column = row, column


class Trip:
    def __init__(self, status: str, start: Location, end: Location, robot_type: str):
        """
        :param status: trip status which can be requested, waiting, started, or finished
        :param start: the start location of the strip
        :param end:  the end location of the trip
        :param robot_type: the type of the requested robot: cozmo or vector
        """
        self.status = status
        self.start, self.end = start, end
        self.robot_type = robot_type


class RobotState:
    def __init__(self, robot_id: int,
                 robot_type: str, x: int, y: int, rotation: int,
                 update_time: datetime = datetime.now(),
                 trip: Trip = None):
        """
        :param robot_id: a unique int for the robot
        :param robot_type: either 'cozmo' or 'vector'
        :param x: the current x position with respect to the robot
        :param y: the current yx position with respect to the robot
        :param rotation: the current rotation with respect to the robot
        :param update_time: the last update time in the server for this robot
        :param trip: The current trip of this robot
        """
        self.robot_id, self.robot_type = robot_id, robot_type
        self.x, self.y, self.rotation = x, y, rotation
        self.update_time = update_time
        self.trip = trip

    def update(self, robot_state):
        self.x = robot_state.x
        self.y = robot_state.y
        self.rotation = robot_state.rotation
        self.update_time = robot_state.update_time
        # update trip status
        if robot_state.trip:
            if robot_state.trip['status'] == 'started':
                self.trip['status'] = robot_state.trip['status']
            if robot_state.trip['status'] == 'finished':
                self.trip = None


class RobotEncoder(json.JSONEncoder):
    def default(self, json_object):
        if isinstance(json_object, datetime):
            return json_object.isoformat()
        if isinstance(json_object, Location):
            return json_object.__dict__
        if isinstance(json_object, Trip):
            return json_object.__dict__
        return json_object.__dict__

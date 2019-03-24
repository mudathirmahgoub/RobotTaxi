import json
from datetime import *


class RobotEncoder(json.JSONEncoder):
    def default(self, json_object):
        if isinstance(json_object, datetime):
            return json_object.isoformat()
        return json_object.__dict__


class RobotState:
    def __init__(self, robot_id, robot_type, x, y, rotation, update_time=datetime.now()):
        self.robot_id, self.robot_type = robot_id, robot_type
        self.x, self.y, self.rotation = x, y, rotation
        self.update_time = update_time


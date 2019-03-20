import threading
import json  # for reading map.json file
from datetime import *
from flask import Flask, jsonify, request, abort, Response

# initialize the server app
app = Flask(__name__, static_folder='app')

# a lock for thread safe id
id_lock = threading.Lock()

# unique id initially is zero
app.unique_id = 0

class RobotState:
    def __init__(self, robot_id, x, y, angle_z_degrees):
        self.robot_id = robot_id
        self.x, self.y, self.angle_z_degrees = x, y, angle_z_degrees
        self.update_time = datetime.now()


# global dictionary for robots that stores robot id and its state
app.robots_dictionary = {}


# GET '/' for testing the server
@app.route('/')
def test():
    return "The server is working."


# GET '/' for testing the server
@app.route('/map')
def get_map():
    with open('map.json') as json_file:
        map_data = json.load(json_file)
        print(map_data)
        return jsonify(map_data)


# GET '/id' returns a unique id from the server
@app.route('/id')
def get_id():
    # acquire the lock before getting a new id
    id_lock.acquire()
    app.unique_id = app.unique_id + 1
    app.robots_dictionary[app.unique_id] = None
    id_lock.release()
    return jsonify({'id': app.unique_id})


# POST '/robot_status/<id>' returns a unique id from the server
@app.route('/robot_status/<int:robot_id>', methods=['POST'])
def post_status(robot_id):
    # abort if robot_id does not exist
    if robot_id not in app.robots_dictionary:
        abort(404, {'message': 'Robot with id {0} does not exist'.format(robot_id)})
    json = request.get_json()
    json['update_time'] = datetime.now()
    return jsonify(json)


if __name__ == '__main__':
    app.run(port=7000, host='0.0.0.0', debug=True)

import threading
from flask import Flask, jsonify, request, abort
from shared import *
from werkzeug.utils import secure_filename
import os

# initialize the server app
app = Flask(__name__, static_folder='app')
app.upload_directory = 'data'
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 12288
app.json_encoder = RobotEncoder

# a lock for thread safe id
id_lock = threading.Lock()

# unique id initially is zero
app.unique_id = 0

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
        return jsonify(map_data)


# GET '/id' returns a unique id from the server
@app.route('/id')
def get_id():
    # acquire the lock before getting a new id
    id_lock.acquire()
    app.unique_id = app.unique_id + 1
    app.robots_dictionary[app.unique_id] = None
    client_directory = app.upload_directory + '/' + str(app.unique_id)
    if not os.path.exists(client_directory):
        os.makedirs(client_directory)
    id_lock.release()
    return jsonify({'id': app.unique_id})


# GET '/robot_status' get the state of all robots
@app.route('/robot_status', methods=['GET'])
def get_all_robots():
    # filter out none values
    robots = {key: value for key, value in app.robots_dictionary.items() if value is not None}
    return jsonify(robots)


# POST '/robot_status/<id>' updates robot status and returns update time
@app.route('/robot_status/<int:robot_id>', methods=['POST'])
def post_status(robot_id):
    # abort if robot_id does not exist
    if robot_id not in app.robots_dictionary:
        abort(404, {'message': 'Robot with id {0} does not exist'.format(robot_id)})
    json_data = request.get_json()
    robot_state = RobotState(**json_data)
    # update the time
    robot_state.update_time = datetime.now()
    # update the dictionary
    app.robots_dictionary[robot_id] = robot_state
    return jsonify(robot_state)


if __name__ == '__main__':
    app.run(port=7000, host='0.0.0.0', debug=True)

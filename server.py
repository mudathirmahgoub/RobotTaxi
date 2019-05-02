import threading
from flask import Flask, jsonify, request, abort
from shared import *
import os
import matlab.engine

# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')


# initialize the server app
app = Flask(__name__, static_folder='app')
app.upload_directory = 'matlab/data'
app.config['UPLOAD_FOLDER'] = 'matlab/data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.json_encoder = RobotEncoder
app.allowed_extensions = {'jpeg'}

# a lock for thread safe id
id_lock = threading.Lock()

# unique id initially is zero
app.unique_id = 0

# global dictionary for robots that stores robot id and its state
app.robots_dictionary = {}
# global dictionary for trips that stores robot id and trip status
app.trips_dictionary = {}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.allowed_extensions


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


@app.route('/classify_image/<int:robot_id>', methods=['POST'])
def classify_image(robot_id):
    if robot_id not in app.robots_dictionary:
        abort(404, {'message': f'Robot with id {robot_id} does not exist'})

    if len(request.files) != 1:
        abort(500, {'message': 'A single image is allowed in the request'})
    file = next(request.files.values())
    if file.filename == '':
        abort(500, {'message': 'No content is uploaded'})
    if file and allowed_file(file.filename):
        client_directory = app.upload_directory + '/' + str(robot_id)
        file.save(os.path.join(client_directory, 'current_image.jpeg'))
        image_class = matlab_engine.classify_image(client_directory.replace('matlab/', ''))
        print(image_class)
        return jsonify({'id': robot_id, 'image_class': image_class})
    abort(500, {'message': f'file {file.filename} not allowed'})


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


# POST '/robot_status/<id>' updates robot status and returns update time
@app.route('/trip', methods=['POST'])
def trip_request():
    trip = request.get_json()
    print(trip)
    selected_robot = get_nearest_robot(trip)
    if not selected_robot:
        abort(404, {'message': 'The trip request can not be fulfilled. Please try again later.'})
    return jsonify(selected_robot)


def get_nearest_robot(trip):
    # filter out none values
    robots = {value for value in app.robots_dictionary.values() if value is not None}
    idle_robots = {robot for robot in robots if robot.trip is None}
    print(idle_robots)
    # no idle robot
    if len(idle_robots) == 0:
        return None

    # find the nearest robot
    idle_robots.sort(key=lambda robot: get_distance(trip, robot))
    trip['status'] = 'started'
    selected_robot = idle_robots[0]
    selected_robot.trip = trip
    print(selected_robot)
    return selected_robot


def get_distance(trip, robot):
    return 1


if __name__ == '__main__':
    app.run(port=7000, host='0.0.0.0', debug=True)

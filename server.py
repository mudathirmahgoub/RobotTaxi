import threading
from flask import Flask, jsonify, request

# initialize the server app
app = Flask(__name__)

# a lock for thread safe id
id_lock = threading.Lock()

# unique id initially is zero
unique_id = 0


# GET '/' for testing the server
@app.route('/')
def test():
    return "The server is working."


# GET '/id' returns a unique id from the server
@app.route('/id')
def get_id():
    global unique_id
    # acquire the lock before getting a new id
    id_lock.acquire()
    unique_id = unique_id +  1
    id_lock.release()
    return jsonify({'id': unique_id})


# POST '/robot_status/<id>' returns a unique id from the server
@app.route('/robot_status/<id>', methods=['POST'])
def post_status(id):
    print(request)
    global unique_id
    pass
    return jsonify({'id': id})


if __name__ == '__main__':
    app.run(port=5000, debug=True)

from flask import Flask, request
from collector.resources import ResMachine

app = Flask(__name__)
host = '0.0.0.0'
port = 5000

machine = ResMachine()

@app.route('/join')
def join_manager():
    pass

@app.post('/get')
def get_state():
    # List of requested machine informations
    paths = request.json['get']

    # Current machine state
    state = machine.collect()

    # Requested machine informations
    res = {}

    for path in paths:
        data = state

        for key in path.split('.'):
            if key in data:
                data = data[key]
                
        res[path] = data

    return res


@app.post('/set')
def set_state():
    pass

app.run(host=host, port=port)

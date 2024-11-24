from flask import Flask, jsonify
from threading import Thread
import logging

def create_app(lap_data):
    app = Flask(__name__)

    @app.route("/get_data", methods=["GET"])
    def get_data():
        return jsonify(lap_data)

    return app

def start_server(lap_data):
    # Start a Flask server for communication
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app = create_app(lap_data)
    server_thread = Thread(target=app.run, kwargs={"port": 5000, "debug": False, "use_reloader": False})
    server_thread.daemon = True
    server_thread.start()

from flask import Flask
from  flask_restful import Api,Resource
from flask_cors import CORS
from meters import Meters
from meter import Meter
from gauge import Gauge

class Server:
    app = None
    api = None
    meter = None

    def __init__(self):
        print("init")
        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(self.app)

if(__name__ == "__main__"):
    TAG = "main:"
    API_VERSION = "/api/v1"
    server = Server()
    server.api.add_resource(Meters, API_VERSION + "/meters")
    server.api.add_resource(Meter, API_VERSION + "/meters/<mid>")
    server.api.add_resource(Gauge, API_VERSION + "/gauge/<mid>")
    server.app.run(host="0.0.0.0", debug=True, port=5000)

    # app.run(host="0.0.0.0", debug=True, port=5000)


from flask import Flask
from  flask_restful import Api,Resource
from flask_cors import CORS
from meters import Meters
from meter import Meter
from gauge import Gauge, Host
from login import Login, Refresh
from create_new_meter import CreateNewMeter
from energy_mng import EnergyMng

import jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

class Server:
    app = None
    api = None
    meter = None

    def __init__(self):
        print("init")
        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(self.app)
        self.app.config['JWT_SECRET_KEY'] = '0x00ff0000'
        # 15 minutes
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 15*600
        self.jwt = JWTManager(self.app)

if(__name__ == "__main__"):
    TAG = "main:"
    API_VERSION = "/api/v1"
    server = Server()
    server.api.add_resource(Meters, API_VERSION + "/meters")
    server.api.add_resource(Meter, API_VERSION + "/meters/<mid>")
    server.api.add_resource(Gauge, API_VERSION + "/gauge/<mid>")
    server.api.add_resource(Login, API_VERSION + "/users/login")
    server.api.add_resource(Refresh, API_VERSION + '/users/refresh')
    server.api.add_resource(CreateNewMeter, API_VERSION + "/meters")
    server.api.add_resource(EnergyMng, API_VERSION + "/energy/<mid>")

    server.api.add_resource(Host, "/")
    server.app.run(host="0.0.0.0", debug=False, port=5000)

    # app.run(host="0.0.0.0", debug=True, port=5000)


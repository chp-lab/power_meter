from flask import Flask, request
from flask_restful import Resource, reqparse
from module import Module
import time
import bcrypt
from database import Database
import jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

class Login(Resource):
    def post(self):
        
        TAG = "login:"
        module = Module()
        database = Database()

        start_time = time.time()
        username_key = "username"
        password_key = "password"
        parser = reqparse.RequestParser()
        parser.add_argument(username_key)
        parser.add_argument(password_key)
        args = parser.parse_args()
        if(not (module.isQueryStr(args, username_key) and module.isQueryStr(args, password_key))):
            print(TAG, "username and password are required")
            return module.unauthorized()
        username = args.get(username_key)
        password = args.get(password_key)
        username = username.replace(" ", "")
        username = username.split("\n")[0]
        password = password.replace(" ", "")
        password = password.split("\n")[0]
        if( (len(username) == 0) or (len(password) == 0) ):
            return module.unauthorized()
        # check with database
        query_cmd = """select username, password from UserInformations where username='%s' """ %(username)
        print(TAG, "query_cmd=", query_cmd)
        response = database.getData(query_cmd)
        print(TAG, "result=", response)
        # check error
        if(response[1] != 200):
            return response
        # user not found
        if(len(response[0]['result']) == 0):
            print(TAG, "user not found!")
            return module.userNotFound()
        user_data = response[0]['result'][0]

        print(TAG, "user_data=", user_data)
        result = {}
        if(len(user_data) > 0):
            #check password
            hashed = user_data['password']
            hashed = hashed.encode('utf8')
            password = password.encode('utf8')
            if (bcrypt.checkpw(password, hashed)):
                iat = time.time()
                print(TAG, "iat=", iat)
                payload = {"iss":"chp-lab", "sub":username, "aud":1}
                result['access_token'] = create_access_token(identity=payload)
                result['refresh_token'] = create_refresh_token(identity=payload)
            else:
                return module.unauthorized()
        else:
            return module.userNotFound()

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
                   'type': True,
                   'message': "success",
                   'elapsed_time_ms': elapsed_time,
                   'len':len(result),
                   'result': result,
               }, 200

class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        TAG = "Refresh:"
        start_time = time.time()

        current_user = get_jwt_identity()
        print(TAG, "current_user=",current_user)
        payload = {"iss": "chp-lab", "sub": "testuid", "aud": 1}
        result = {
            'access_token':create_access_token(identity=payload),
            'refresh_token':create_refresh_token(identity=payload)
        }

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
                   'type': True,
                   'message': "success",
                   'elapsed_time_ms': elapsed_time,
                   'len': len(result),
                   'result': result,
               }, 200

    
from flask import Flask, request
from flask_restful import Resource, reqparse
from module import Module
import bcrypt
from database import Database
import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
import time


class CreateNewMeter(Resource):
    @jwt_required
    def post(self):
        TAG = "CreateNewMeter:"
        module = Module()
        database = Database()
        start_time = time.time()
        parser = reqparse.RequestParser()
        parser.add_argument("meter_id")
        parser.add_argument("meter_name")
        parser.add_argument("department")
        parser.add_argument("user_account")
        args = parser.parse_args()
        current_user = get_jwt_identity()
        username = current_user['sub']

        if (not (module.isQueryStr(args, "meter_id") and module.isQueryStr(args, "meter_name")
                 and module.isQueryStr(args, "department") and module.isQueryStr(args, "user_account"))):
            print(TAG, "meter_id, meter_name and department are required")
            return {
                       'type': False,
                       'message': "fail",
                       'error_message': "user_account, meter_id, meter_name and department are required",
                       'result': None
                   }, 400

        meterID = args.get("meter_id")
        meterName = args.get("meter_name")
        department = args.get("department")
        user_account = username

        print(TAG, "meterID=", meterID)

        cmd = """SELECT adminID FROM DashaAdmin WHERE adminID='%s' AND level='WRE' """ % (username)
        res = database.getData(cmd)
        # print(TAG, "res=", res)
        if (res[0]["len"] == 0):
            return module.unauthorized()
        cmd = """SELECT machineID FROM Machines WHERE machineID='%s' """ % (meterID)
        res = database.getData(cmd)
        print(TAG, "res=", res)
        if (res[0]["len"] > 0):
            return module.meterExist()

        cmd = """INSERT INTO Machines(machineID, machineName, department, username)
        VALUES('%s', '%s', '%s', '%s')""" % (meterID, meterName, department, user_account)
        print(TAG, "cmd=", cmd)
        print(TAG, "success=", res)
        res = database.insertData(cmd)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
        return res

    @jwt_required
    def delete(self):
        TAG = "MeterDelete:"
        module = Module()
        start_time = time.time()


        database = Database()
        module = Module()

        current_user = get_jwt_identity()
        print(TAG, "current_user=", current_user)

        # print(TAG, "username=", current_user["sub"])
        username = current_user['sub']

        args = request.args

        if(not module.isQueryStr(args, "meter_id")):
            return module.wrongAPImsg()
        meter_id = args["meter_id"]


        cmd = """SELECT machineID, machineName, department FROM Machines 
        WHERE username='%s' AND machineID='%s' """ % (username, meter_id)

        res = database.getData(cmd)

        if(res[0]['len'] == 0):
            return module.measurementNotFound()

        cmd = """DELETE FROM Machines WHERE username='%s' AND machineID='%s' """ % (username, meter_id)

        res = database.insertData(cmd)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
            "type": True,
            "message":"success",
            "elapsed_time_ms": elapsed_time,
            "result": "meter " + meter_id + "deleted"
        }


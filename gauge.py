import time
from module import *
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from meter import Meter

class Gauge(Resource):
    @jwt_required
    def get(self, mid):
        TAG = "Gauge:"
        module = Module()
        meter = Meter()
        start_time = time.time()

        current_user = get_jwt_identity()
        username = current_user['sub']
        if(not meter.isUserHasPerm(username, mid)):
            return module.unauthorized()
        args = request.args
        param = "V0, V1, V2, I0, I1, I2, pf0, pf1, pf2, P0, P1, P2, f0, f1, f2, E0, E1, E2"
        if(module.isQueryStr(args, "parameters")):
            param = args["parameters"]
            param = param.replace(" ", ", ")
            # print(TAG, "param=", param)
        command = """SELECT %s FROM %s ORDER BY DESC LIMIT 1 """ % (param, mid)
        # print(TAG, "cmd=", command)
        if (not module.isMeterExist(mid)):
            return module.measurementNotFound()
        res = module.getData(command)
        # print(TAG, "res=", res)
        results = {
            "meter_id": "",
            "parameters": [],
            "values": []
        }
        gauge_data = {}
        if(len(res) > 0):
            tmp_res = res[0]
            results["meter_id"] = tmp_res["name"]
            results["parameters"] = tmp_res["columns"]
            results["values"] = tmp_res["values"]
        else:
            return module.measurementNotFound();

        for i in range(len(results["parameters"])):
            param_name = results["parameters"][i]
            # print(TAG, "param_name=", param_name)
            gauge_data[param_name] = results["values"][0][i]
        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
        return {
            "type": True,
            "message":"success",
            "elapsed_time_ms": elapsed_time,
            "result": gauge_data
        }

class Host(Resource):
    def get(self):
        TAG = "Host:"
        return {
            "type":True,
            "message":"Success",
            "help":"API work well"
        }
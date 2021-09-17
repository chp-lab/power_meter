import time
from module import Module
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from meter import Meter

class EnergyMng(Resource):
    @jwt_required
    def get(self, mid):
        TAG = "energy_mng:"
        start_time = time.time()
        print(TAG, "energy mng recv")
        module = Module()
        meter = Meter()
        current_user = get_jwt_identity()
        print(TAG, "current_user=", current_user)

        username = current_user['sub']
        perm = meter.isUserHasPerm(username, mid)
        if(not perm):
            return module.unauthorized()
        args = request.args

        print(TAG, "user permitted")
        if(not module.isMeterExist(mid)):
            print(TAG, "meter not found")
            return module.measurementNotFound()

        time_cmd = """SELECT MONTH(CURRENT_DATE) AS CUR_MONTH"""
        cur_month = time_cmd[0]['result'][0]['CUR_MONTH']

        for i in range(1, cur_month):
            start_date = ""
            end_date = ""
            if(i < 10):
                start_date = "2021-0%s-01 00:00:00" %(i)
                end_date = "2021-0%s-27 23:59:59" %(i)
            else:
                start_date = "2021-%s-01 00:00:00" %(i)
                end_date = "2021-%s-27 23:59:59" %(i)
            print(TAG, "start_date=", start_date)
            print(TAG, "end_date=", end_date)

        command = """SELECT E0, E1, E2, time 
        FROM mm_600194433DCF 
        WHERE (time > '2021-08-01 00:00:00') AND (time < '2021-08-27 23:59:59') 
        ORDER BY time DESC LIMIT 1"""

        print(TAG, "cmd=", command)

        res = module.getData(command)

        print(TAG, "res=", res)

        all_result = []

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
            return module.measurementNotFound()

        for i in range(len(results["parameters"])):
            param_name = results["parameters"][i]
            # print(TAG, "param_name=", param_name)
            gauge_data[param_name] = results["values"][0][i]

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        all_result.append(gauge_data)

        return {
            "type": True,
            "message":"success",
            "elapsed_time_ms": elapsed_time,
            "result": all_result
        }
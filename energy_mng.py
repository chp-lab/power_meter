import time
from module import Module
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from meter import Meter
from database import Database

class EnergyMng(Resource):
    @jwt_required
    def get(self, mid):
        TAG = "energy_mng:"

        start_time = time.time()
        print(TAG, "energy mng recv")
        module = Module()
        meter = Meter()
        current_user = get_jwt_identity()
        database = Database()

        print(TAG, "current_user=", current_user)

        username = current_user['sub']
        perm = meter.isUserHasPerm(username, mid)
        if(not perm):
            return module.unauthorized()
        args = request.args
        if not ( module.isQueryStr(args, "year")):
            return module.wrongAPImsg()
        year = args["year"]
        year = int(year)

        # if not (isinstance(year, int)):
        #     return module.wrongAPImsg()

        print(TAG, "user permitted")
        if(not module.isMeterExist(mid)):
            print(TAG, "meter not found")
            return module.measurementNotFound()

        time_cmd = """SELECT MONTH(CURRENT_DATE) AS CUR_MONTH"""
        time_res = database.getData(time_cmd)
        cur_month = time_res[0]['result'][0]['CUR_MONTH']

        all_result = []

        mounts_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul","Aug", "Sep", "Oct", "Nov", "Dec"]

        for i in range(1, cur_month):
            start_date = ""
            end_date = ""
            if(i < 10):
                start_date = "%s-0%s-01 00:00:00" % (year, i)
                end_date = "%s-0%s-27 23:59:59" % (year, i)
            else:
                start_date = "%s-%s-01 00:00:00" % (year, i)
                end_date = "%s-%s-27 23:59:59" % (year, i)
            # print(TAG, "start_date=", start_date)
            # print(TAG, "end_date=", end_date)

            command = """SELECT E0, E1, E2, time 
            FROM %s 
            WHERE (time > '%s') AND (time < '%s') 
            ORDER BY time DESC LIMIT 1""" % (mid, start_date, end_date)

            # print(TAG, "cmd=", command)

            res = module.getData(command)

            print(TAG, "res=", res)

            results = {
                "meter_id": "",
                "parameters": [],
                "values": []
            }

            print(TAG, "res=", res)

            gauge_data = {}

            if(len(res) > 0):
                tmp_res = res[0]
                results["meter_id"] = tmp_res["name"]
                results["parameters"] = tmp_res["columns"]
                results["values"] = tmp_res["values"]
                for i in range(len(results["parameters"])):
                    param_name = results["parameters"][i]
                    # print(TAG, "param_name=", param_name)
                    gauge_data[param_name] = results["values"][0][i]
            else:
                gauge_data = {
                    "E0": 0,
                    "E1": 0,
                    "E2": 0,
                    "time": end_date
                }

            gauge_data["month_name"] = mounts_name[i - 1]
            gauge_data["month_num"] = i

            all_result.append(gauge_data)

        last_year = year - 1
        last_year_cmd = """SELECT E0, E1, E2, time 
        FROM mm_600194433DCF 
        WHERE (time > '%s-01-01 00:00:00') AND (time < '%s-12-31 23:59:59') 
        ORDER BY time DESC LIMIT 1""" % (last_year, last_year)

        last_year_rec = module.getData(last_year_cmd)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": elapsed_time,
            "result": all_result
        }
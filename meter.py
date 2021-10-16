import time
from module import Module
from flask import request
from flask_restful import Resource
import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import Database

class Meter(Resource):
    def isUserHasPerm(self, username, mid):
        TAG = "isUserHasPerm:"
        database = Database()
        cmd = """SELECT machineID from Machines WHERE username='%s' AND machineID='%s' """ %(username, mid)
        res = database.getData(cmd)
        if(res[1] == 200):
            if(len(res[0]['result']) > 0):
                return True
            else:
                return False

    @jwt_required
    def get(self, mid):
        TAG = "Meter:"
        module = Module()
        try:
            current_user = get_jwt_identity()
        except:
            return module.unauthorized()
        print(TAG, "current_user=", current_user)

        username = current_user['sub']

        perm = self.isUserHasPerm(username, mid)

        if(not perm):
            return module.unauthorized()

        start_time = time.time()
        cur_date = datetime.datetime.now()
        st = cur_date.strftime("%Y-%m-%d 00:00:00")
        et = cur_date.strftime("%Y-%m-%d 23:59:59")
        print(TAG, "st=", st)
        print(TAG, "et=", et)
        args = request.args

        if(module.isQueryStr(args, "start")):
            st = args["start"]
            print(TAG, "custom start date=", st)
            # command = command + """AND TIME >= '%s' """ %(st)
        if(module.isQueryStr(args, "end")):
            et = args["end"]
            print(TAG, "custom end date=", et)
            # command = command + """AND TIME <= '%s' """ %(et)
        param = "V0, V1, V2, I0, I1, I2, pf0, pf1, pf2, P0, P1, P2, f0, f1, f2, E0, E1, E2"
        if(module.isQueryStr(args, "parameters")):
            param = args["parameters"]
            param = param.replace(" ", ", ")
            print(TAG, "param=", param)
        command = """SELECT %s FROM %s WHERE TIME >= '%s' AND TIME <= '%s' """ %(param, mid, st, et)
        print(TAG, "cmd=", command)
        if(not module.isMeterExist(mid)):
            return module.measurementNotFound()
        
        res = module.getData(command)
        # print(TAG, res)
        results = {
            "meter_id":"",
            "parameters":[],
            "values":[]
        }
        if(len(res) > 0):
            tmp_res = res[0]
            results["meter_id"] = tmp_res["name"]
            results["parameters"] = tmp_res["columns"]
            results["values"] = tmp_res["values"]
        else:
            return module.measurementNotFound();

        graph_data = {}
        for i in range(1, len(results["parameters"])):
            # print(TAG, "i=", i)
            tmp_max = 0;
            tmp_min = 1000000;
            parameter = results["parameters"][i]
            # print(TAG, "parameter=", parameter)
            x_series = []
            y_series = []
            for j in range(len(results["values"])):
                x_v = results["values"][j][0]
                x_v = x_v.split(".")[0]
                x_v = x_v.replace("T", " ")
                x_series.append(x_v)
                y_series.append(results["values"][j][i])
                tmp_y = results["values"][j][i]
                if(tmp_y > tmp_max):
                    tmp_max = tmp_y

                if(tmp_y < tmp_min):
                    tmp_min = tmp_y

            graph_data[parameter] = {"x": x_series, "y": y_series}
            graph_data[parameter]["max"] = tmp_max
            graph_data[parameter]["min"] = tmp_min

        # print(TAG, "res=", res)
        # print(TAG, "name=", meter_name)
        # print(TAG, "columns=", meter_columns)
        # for row in meter_values:
        #     print(TAG, "row=", row)

        elapsed_time = (time.time() - start_time)*1000
        print(TAG, "times=", elapsed_time, "ms")
        return {
            "type": True,
            "message":"success",
            "elapsed_time_ms": elapsed_time,
            "result": graph_data
        }
if (__name__ == "__main__"):
    meter = Meter()
    meter.get("mm20050001")
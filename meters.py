import time
from module import Module
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from database import Database
from flask_jwt_extended import get_jwt_identity

class Meters(Resource):
    @jwt_required
    def get(self):
        TAG = "Meters:"
        module = Module()
        start_time = time.time()
        database = Database()
        module = Module()

        current_user = get_jwt_identity()
        print(TAG, "current_user=",current_user)
        
        # print(TAG, "username=", current_user["sub"])
        username = current_user['sub']

        cmd = """SELECT machineID, machineName, department FROM Machines WHERE username='%s' """ %(username)
        res = database.getData(cmd)


        # command = "show measurements"
        # res = module.getData(command)[0]["values"]
        # print(TAG, "res=", res)
        # meters = []
        # for meter in res:
        #     tmp_meter = {}
        #     # print(TAG, meter[0])
        #     tmp_meter["id"] = meter[0]
        #     meters.append(tmp_meter)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")

        return res
        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": elapsed_time,
            "len": len(meters),
            "result": meters
        }
    def structure(self):
        TAG = "Meters:"
        module = Module()
        start_time = time.time()
        command = "show measurements"
        res = module.getData(command)[0]
        print(TAG, "res=", res)
        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
        return {
            "type": True,
            "message": "success",
            "elapsed_time_ms": elapsed_time,
            "len": len(res),
            "result": res
        }
if (__name__ == "__main__"):
    meters = Meters()
    meters.get()
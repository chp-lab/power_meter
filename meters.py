import time
from module import *
from flask_restful import Resource

class Meters(Resource):
    def get(self):
        TAG = "Meters:"
        module = Module()
        start_time = time.time()
        command = "show measurements"
        res = module.getData(command)[0]["values"]
        print(TAG, "res=", res)
        meters = []
        for meter in res:
            tmp_meter = {}
            # print(TAG, meter[0])
            tmp_meter["id"] = meter[0]
            meters.append(tmp_meter)

        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
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
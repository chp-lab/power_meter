from module import Module
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from meter import Meter

class EnergyMng(Resource):
    @jwt_required
    def get(self, mid):
        TAG = "energy_mng:"
        module = Module()
        meter = Meter()
        current_user = get_jwt_identity()
        print(TAG, "current_user=", current_user)

        username = current_user['sub']
        perm = meter.isUserHasPerm(username, mid)
        if(not perm):
            return module.unauthorized()
        args = request.args
        year = args["year"]

        if(not module.isMeterExist(mid)):
            return module.measurementNotFound()

        command = """SELECT E0, E1, E2, time 
        FROM mm_600194433DCF 
        WHERE (time > '2021-08-01 00:00:00') AND (time < '2021-08-27 23:59:59') 
        ORDER BY time DESC LIMIT 1"""

        res = module.getData(command)

        print(TAG, "res=", res)

        return "test"
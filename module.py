from influxdb import InfluxDBClient

class Module():
    def __init__(self):
        print("Creating new modules")
    def getData(self, query_str):
        TAG = "getData:"
        print(TAG, query_str)
        client = InfluxDBClient('localhost', 8086, 'chp-lab', 'atop3352', 'envdb')
        result = client.query(query_str)
        json_res = result.raw
        json_res = json_res['series']
        print(TAG, "json_res=", json_res)
        client.close()
        return json_res
    def isMeterExist(self, mid):
        TAG = "isMeterExist:"
        res = self.getData("select * from %s limit 1" %mid)
        if(len(res) == 0):
            print(TAG, "measurement not found")
            return False
        else:
            return True

    def measurementNotFound(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Measurement Not Found",
                   'result': None
               }, 404

    def serveErrMsg(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Internal Server Error",
                   'result': None
               }, 500

    def isQueryStr(self, args, key):
        TAG = "isQueryStr:"
        # print(TAG, "args=", args, type(args))
        if ((args.get(key) is not None) and (len(args.get(key)) > 0)):
            return True
        else:
            return False

    def unauthorized(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Unauthorized",
                   'result': None
               }, 401

    def userNotFound(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "User not found",
                   'result': None
               }, 404

    def isValidToken(self, current_user):
        if("sub" not in current_user):
            return False
        else:
            return True

    def wrongAPImsg(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "wrong API calling. Check related parameter e.g. query string, url etc.",
                   'result': None
               }, 400
    def meterExist(self):
        return {
                   'type': False,
                   'message': "fail",
                   'error_message': "Meter exist",
                   'result': None
               }, 400

if (__name__ == "__main__"):
    module = Module()
    command = "select * from mm20050001 limit 2"
    res = module.getData(command)[0]
    meter_name = res["name"]
    meter_columns = res["columns"]
    meter_values = res["values"]
    print(res)
    print(meter_columns)
    # print(meter_values)
    for i in range(len(meter_values)):
        print(meter_values[i])
    # print(res)


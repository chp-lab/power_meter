from flask import Flask, request
from flask_restful import Resource
import mysql.connector
import time
import datetime
from module import Module

class Database(Resource):
    config = {}
    def __init__(self):
        TAG = "Database:"
        self.config = {
            'host': '18.140.173.239',
            'user': 'admin',
            'passwd': '0x00ff0000',
            'database': 'chplab',
            'use_unicode': True,
            'charset': 'utf8'
        }

    def getData(self, query_cmd):
        TAG = "Database:"
        start_time = time.time()
        # self.__init__()
        # establish mysql connection
        module = Module()
        # print(TAG, self.config)
        # print(TAG, "Loading data from mysql server")
        mydb = mysql.connector.connect(**self.config)
        # print(TAG, "Database is ready")
        mycursor = mydb.cursor()
        # print(TAG, "Cursor is ready")
        # execute the sql command
        try:
            # print(TAG, "trying to execute command")
            mycursor.execute(query_cmd)
        except Exception as err:
            # on error execute
            print(TAG, "error on execute command")
            print(TAG, err)
            mydb.close()
            return module.serveErrMsg()
        # get raw result
        myresult = mycursor.fetchall()
        # get columns name
        column_name = mycursor.column_names
        # print(TAG, "myresult=", myresult)
        # print(TAG, "columns name=", column_name)
        # convert raw result to json format
        result = []
        for row in myresult:
            tmp_res = {}
            for i in range(len(column_name)):
                if (isinstance(row[i], datetime.date)):
                    # print(TAG, "date found")
                    tmp_res[column_name[i]] = str(row[i])
                elif (isinstance(row[i], bytes)):
                    tmp_json = json.loads(row[i].decode())
                    tmp_res[column_name[i]] = tmp_json
                else:
                    # print(TAG, "type=", type(row[i]))
                    tmp_res[column_name[i]] = row[i]
            result.append(tmp_res)
        # close mysql connecttion
        mydb.close()
        # calculate elapset time
        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
        # reture result to the client
        return {
                   'type': True,
                   'message': "success",
                   'error_message': None,
                   'len': len(result),
                   'result': result,
                   'elapsed_time_ms': elapsed_time
               }, 200

    def insertData(self, query_cmd):
        TAG = "Database:"
        start_time = time.time()
        # self.__init__()
        # establish mysql connection
        module = Module()
        # print(TAG, self.config)
        # print(TAG, "Loading data from mysql server")
        mydb = mysql.connector.connect(**self.config)
        # print(TAG, "Database is ready")
        mycursor = mydb.cursor()
        # print(TAG, "Cursor is ready")
        # execute the sql command
        try:
            # print(TAG, "trying to execute command")
            mycursor.execute(query_cmd)
        except Exception as err:
            # on error execute
            print(TAG, "error on execute command")
            print(TAG, err)
            mydb.close()
            return module.serveErrMsg()
        mydb.commit()
        mydb.close()
        # calculate elapset time
        elapsed_time = (time.time() - start_time) * 1000
        print(TAG, "times=", elapsed_time, "ms")
        return {
                   'type': True,
                   'message': "success",
                   'error_message': None,
                   'result': "Meter created",
                   'elapsed_time_ms': elapsed_time
               }, 200

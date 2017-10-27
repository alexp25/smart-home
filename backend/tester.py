from flask import Flask
from flask import render_template, send_file, session, Response, request, make_response, send_from_directory
from flask import jsonify
import json
import datetime
import os
import subprocess
import copy
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
# gevent.monkey.patch_time()
gevent.monkey.patch_all(socket=True, dns=True, time=True, select=True, thread=False, os=False, ssl=True, httplib=False, subprocess=False, sys=False, aggressive=True, Event=False, builtins=True, signal=False)
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from AppModules.DebugPrintThread import DebugPrintThread
import appVariables
# only the main modules calls init
# the other modules using the global variables just import "appVariables"
appVariables.init()

from bson import json_util
from Modules.mongo_db import MongoManager
mongomanager = MongoManager()
mongomanager.connect()

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/find')
def find():
    result = mongomanager.find("test","test2",None)
    return result

@app.route('/insert',methods=['POST'])
def insert():
    print(request.json)
    # document = json.dumps(request.json)
    # print(document)
    document=request.json
    result = mongomanager.insert("test","test2",document)
    # result = json.dumps({"result":1})
    return result

@app.route('/pipeline')
def averageq():
    pipeline = [{"$match": {"s_id": 132, "ts": {"$gt": "2017-02-18 17:04:38.146000"}}},
                 {"$group": {"_id": "$s_id", "avg": {"$avg": "$value"}}}
                ]
    result = mongomanager.aggregate_pipeline("mydb","sensor_data", pipeline)
    print(result)
    return json.dumps(result, default=json_util.default)



if __name__ == '__main__':
    print('tester started')
    thread5 = DebugPrintThread()
    thread5.start()

    server = pywsgi.WSGIServer(('0.0.0.0', 8100), app, handler_class=WebSocketHandler)
    server.serve_forever()
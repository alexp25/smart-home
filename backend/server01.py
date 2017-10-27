# python modules
from flask import Flask
from flask import render_template, send_file, session, Response, request, make_response, send_from_directory, redirect
from flask import jsonify
import json
import datetime
import os
import subprocess
import copy
import time
from dateutil.parser import parse
import sys
#auto generate passwords
import random
import string
#send email
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText
from multiprocessing import Process, Queue
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_time()
# gevent.monkey.patch_all(socket=True, dns=True, time=True, select=True, thread=False, os=False, ssl=True, httplib=False, subprocess=False, sys=False, aggressive=True, Event=False, builtins=True, signal=False)
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
#cross origin requests
from flask_cors import CORS, cross_origin
import threading

from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask_socketio import disconnect

# app modules
import appVariables
# only the main modules calls init
# the other modules using the global variables just import "appVariables"
appVariables.init()
appVariables.myList=['test1','test2']

from AppModules.DebugPrintThread import DebugPrintThread
from AppModules.DataBucketThread import DataBucketThread
from AppModules.SoundDataThread import SoundDataThread
from AppModules.ServerStatusThread import ServerStatusThread
from AppModules.TCPServerThread import TCPServerThread
from AppModules.ControlSystemsThread import ControlSystemsThread
from AppModules.IrrigationControlThread import IrrigationControlThread
from AppModules.DatabaseManagerProcess import DatabaseManagerProcess


# test
from AppModules.TCPServerAsync import simple_tcp_server

if appVariables.appConfig['rpi'] == True:
    from Modules.camerapi_opencv import Camera1
    from AppModules.camera_remote import Camera2
    from Modules.audio_a import audioAnalyzer

    if appVariables.appConfig['ws_connection']=='serial':
        from Modules.serial_com import serialCom
        serialcom = serialCom('/dev/rfcomm1', 38400)
        serialcom.start()
else:
    from Modules.camerapi_sim import Camera1

from Modules.serverCmd import serverCmd

server_cmd = serverCmd()


if appVariables.appConfig['mongo'] == True:
    from Modules.mongo_db import MongoManager
    appVariables.mongomanager = MongoManager()
    appVariables.mongomanager.connect()
    from bson import json_util

# app config
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
# app = Flask('myapp', template_folder=tmpl_dir)
static_folder = "dist"
app = Flask(__name__,static_folder=static_folder, template_folder=tmpl_dir)
CORS(app, supports_credentials=True,resources=r'/api/*')
# CORS(app)
if appVariables.appConfig['rpi'] == False:
    app.debug = True
##    app.config['UPLOAD_FOLDER']="user_data"
#tcp
sockets = Sockets(app)
socketio = SocketIO(app)

def load_node_model():
    m=[]
    with open('config/node_model.json') as f:
        file_contents = f.read()
    try:
        m = json.loads(file_contents)
    except:
        print('node model file exception')
    finally:
        return m

appVariables.clientModelDB = load_node_model()


if not appVariables.appConfig['rpi']:
    with open('config/node_list_test_v2.json') as f:
        file_contents = f.read()
    try:
        appVariables.clientList = json.loads(file_contents)
        t1=time.time()
        for i in range(len(appVariables.clientList)):
            client = appVariables.clientList[i]
            newClientFcn = copy.deepcopy(appVariables.clientModelFcn)
            newClientFcn['connection'] = None
            newClientFcn['q_in'] = Queue(maxsize=10)
            newClientFcn['q_out'] = Queue(maxsize=10)
            newClientFcn['t0'] = t1
            newClientFcn['t0_polling'] = t1
            newClientFcn['t0_log'] = t1
            appVariables.clientListFcn.append(newClientFcn)
            appVariables.clientInfoList.append({'id': client['id'], 'ip': client['ip'], 'type': client['type']})
    except:
        print('node list test file exception')


def read_virtual_nodes():
    virtualNodeList=[]
    virtualNodeListFcn=[]
    virtualNodeInfoList=[]
    with open('config/virtual_nodes.json') as f:
        file_contents = f.read()
    try:
        virtualNodeList = json.loads(file_contents)
        for i in range(len(virtualNodeList)):
            virtualNodeInfoList.append({
                'id': virtualNodeList[i]['id'],
                'type': virtualNodeList[i]['type'],
                'ip': virtualNodeList[i]['ip'],
            })
            newVirtualNode = copy.deepcopy(appVariables.virtualNodeModelFcn)
            newVirtualNode["q_out"] = Queue(maxsize=5)
            virtualNodeListFcn.append(newVirtualNode)
    except:
        appVariables.print_exception('virtual node list file ')
    finally:
        return [virtualNodeList,virtualNodeListFcn,virtualNodeInfoList]



[appVariables.virtualNodeList, appVariables.virtualNodeListFcn, appVariables.virtualNodeInfoList] = read_virtual_nodes()

def request_db(req):
    data=['',None]
    t0=time.time()
    while appVariables.qDatabaseIn.full():
        time.sleep(0.1)
    appVariables.qDatabaseIn.put(req)
    if appVariables.appConfig['blocking_db']:
        while (data[0] != req[0]):
            data = appVariables.qDatabaseOut.get(block=True,timeout=10)
    else:
        while (data[0] != req[0]):
            time.sleep(0.1)
            if time.time() - t0 > appVariables.db_timeout:
                break
            # data = appVariables.qDatabaseOut.get(block=True, timeout=10) #blocking
            if not appVariables.qDatabaseOut.empty():
                # data = appVariables.qDatabaseOut.get(block=False)
                data = appVariables.qDatabaseOut.get(block=False)
    return data


@socketio.on('disconnect_request')
def disconnect_request(message):
    # session['receive_count'] = session.get('receive_count', 0) + 1
    print('disconnect')
    disconnect()

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('ws_control_set')
def wscontrolcommands_socketio(message):
    # print(message)
    try:
        jsondata = json.loads(message)
        getcommands_appdata(jsondata)
    except:
        appVariables.print_exception("[sockets][/app-data]")

@socketio.on('ws_control_get')
def wscontrol_socketio(message):
    jsondata = getdata_appdata(0)
    socketio.emit('ws_control_data',json.dumps(jsondata))

@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        msg = "[sockets][/echo] " + message
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        ws.send(message)

@sockets.route('/broadcast')
def broadcast_socket(ws):
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[sockets][/broadcast] " + "open"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        while not ws.closed:
            gevent.sleep(0.1)
            message = ws.receive()
            if not ws.closed:
                ws.send(message)
        msg = "[sockets][/echo] " + "close"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)


def getdata_appdata(counter):
    jsondata = {
        'info': 'no data',
        'connection': False,
    }
    count_retry = 0
    dt = datetime.datetime.now()
    tm = str(dt.hour).zfill(2) + ":" + str(dt.minute).zfill(2) + ":" + str(dt.second).zfill(2)
    while True:
        try:
            t0 = time.time()
            data = False
            time.sleep(0.01)
            if appVariables.queue_ws_app_data.empty() == False:
                data = appVariables.queue_ws_app_data.get(block=False)
            # data="211,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
            if data != False:
                str1 = data
                string = str1
                stringArray = string.split(",")
                a = [0] * len(stringArray)
                for i in range(len(stringArray)):
                    try:
                        a[i] = int(stringArray[i])
                    except:
                        a[i] = 0
                if a[0] == 211:
                    count_retry = 0
                    systemTime = (stringArray[1].zfill(2) + ':' + stringArray[2].zfill(2) + ':' + stringArray[3].zfill(2))
                    systemOffRem = (stringArray[4].zfill(2) + ':' + stringArray[5].zfill(2) + ':' + stringArray[6].zfill(2))
                    systemOnRem = (stringArray[7].zfill(2) + ':' + stringArray[8].zfill(2) + ':' + stringArray[9].zfill(2))
                    jsondata = {
                        'commandCode': a[0],
                        'counter': counter,
                        'systemTime': systemTime,
                        'serverTime': tm,
                        'systemOffRem': systemOffRem,
                        'systemOnRem': systemOnRem,
                        'mode': a[20],
                        'fault': a[19],
                        'message': string,
                        'pumpCmd': a[10],
                        'carriageCmd': a[11],
                        'carriagePos': a[12],
                        'carriageSpeed': a[13],
                        'sa': a[17],
                        'sb': a[18],
                        'tank': a[15],
                        'light': a[16],
                        'currentPlant': a[14],
                        'wateringFlag': a[22],
                        'log': appVariables.server_commands['log'],
                        'spab': appVariables.server_commands['spab']
                    }

                    return jsondata
            else:
                jsondata = {
                    'info': 'no data',
                    'connection': True
                }
                count_retry = count_retry + 1
                if count_retry >= 100:
                    count_retry = 0
                    msg = "[sockets][/app-data] " + " no data"
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                    return jsondata
        except:
            appVariables.print_exception("[sockets][/app-data]")
            return jsondata

def getcommands_appdata(jsondata):
    if jsondata['cmdcode'] != False:
        if jsondata['cmdcode'] == 'SERVER_CMD':
            sc = jsondata['data']
            if sc['cmd'] == 'LOG_ON':
                appVariables.server_commands['log'] = True
            if sc['cmd'] == 'LOG_OFF':
                appVariables.server_commands['log'] = False
            if sc['cmd'] == 'SPAB_ON':
                appVariables.server_commands['spab'] = True
            if sc['cmd'] == 'SPAB_OFF':
                appVariables.server_commands['spab'] = False

        elif jsondata['cmdcode'] == 'SERVER_PARAMS':
            sc = jsondata['data']
            ##                        sc = json.dumps(sc)
            appVariables.server_params['spab_um'] = sc['spab_um']
            appVariables.server_params['spab_du'] = sc['spab_du']

        else:
            cmdText = jsondata['cmdcode']
            body = jsondata['data']

            cmd = appVariables.systemSettings['codeTable'][cmdText]
            cmdcode = cmd['cmd']

            msg = "[sockets][/app-data] " + cmdText + " " + body
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

            cmd_string = str(cmdcode) + ',' + body

            if not appVariables.wsOutQueue.full():
                appVariables.wsOutQueue.put(cmd_string)

@sockets.route('/app-data')
def appdata_socket(ws):
    counter_poll = 0
    n = 10
    count_retry = 0
    t0=time.time()

    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[sockets][/app-data] " + "open"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        while not ws.closed:
            message = ws.receive()
            try:
                jsondata=json.loads(message)
                getcommands_appdata(jsondata)
            except:
                appVariables.print_exception("[sockets][/app-data]")

            counter_poll = counter_poll + 1
            jsondata = getdata_appdata(counter_poll)
            if not ws.closed:
                ws.send(json.dumps(jsondata))
        msg = "[sockets][/app-data] " + "close"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        appVariables.server_commands = copy.copy(appVariables.server_commands_default)



def sync_device_controls(clientList):
    sync_types=["value","slider"]
    # for each client
    # print json.dumps(clientList, indent=2)
    try:
        for client in clientList:
            if client['commands']!=False:
                # for each command
                for cmd in client['commands']:
                    if client['sdata'] != False:
                        # for each data
                        for data in client['sdata']:
                            if (cmd['type'] in sync_types) and (cmd['code']==data['id']):
                                cmd['value']=data['value']
                                break
    except:
        appVariables.print_exception("sync device controls")

    return clientList

def getdata_appdata_monitorview(params,counter_poll):
    jsondata = {
        'info': 'no data',
        'connection': False,
    }
    t0 = time.time()

    while True:
        gevent.sleep(0.01)
        dt = time.time() - t0
        # if (dt >= 0.1) or (appVariables.flags["new_client_data"] and dt >= 0.01):
        if (dt >= 0.1):
            t0 = time.time()
            appVariables.flags["new_client_data"] = False
            try:
                dt = datetime.datetime.now()
                tm = str(dt.hour).zfill(2) + ":" + str(dt.minute).zfill(2) + ":" + str(dt.second).zfill(2)

                info = '<span>' + str(counter_poll) + '&emsp;Server time: ' + tm + \
                       '</span>'

                fullClientList = appVariables.clientList + appVariables.virtualNodeList
                fullClientInfoList = appVariables.clientInfoList + appVariables.virtualNodeInfoList


                if params is None:
                    # type,id,ip
                    jsondata = {
                        'counter': counter_poll,
                        'info': info,
                        'clientList': fullClientInfoList
                    }
                else:
                    # type,id,ip
                    if params['nodeId'] == -1:
                        jsondata = {
                            'counter': counter_poll,
                            'info': info,
                            'clientList': fullClientInfoList,
                            'clientData': fullClientList
                        }
                    else:
                        if params['nodeId'] > len(fullClientList):
                            jsondata = {
                                'counter': counter_poll,
                                'info': info,
                                'clientList': fullClientInfoList
                            }
                        else:
                            jsondata = {
                                'counter': counter_poll,
                                'info': info,
                                'clientList': fullClientInfoList,
                                'clientData': fullClientList[params['nodeId']]
                            }
                return jsondata
            except:
                appVariables.print_exception("[sockets][/app-data/monitor-view]")
                return jsondata

def getcommands_appdata_monitorview(jsondata):
    params = None
    if jsondata['cmdcode'] != False:
        if jsondata['cmdcode'] == 'SERVER_CMD':
            params = jsondata['data']
            msg = "[sockets][/app-data/monitor-view] " + jsondata["cmdcode"] + " " + params["cmd"]
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)
            if params['cmd'] == 'SYNC_DEVICE_CONTROLS':
                appVariables.clientList = sync_device_controls(appVariables.clientList)

        elif jsondata['cmdcode'] == 'SERVER_PARAMS':
            params = jsondata['data']

        elif jsondata['cmdcode'] == 'SERVER_REQUEST':
            params = jsondata['data']

        elif jsondata['cmdcode'] == 'DEVICE_CMD':
            params = jsondata['data']
            nodeId = int(params['nodeId'])
            for i in range(len(appVariables.clientList)):
                if appVariables.clientList[i]['id'] == nodeId:
                    c_out = "error: queue full!"
                    if not appVariables.clientListFcn[i]['q_out'].full():
                        c_out = params['fback']
                        # new_data = appVariables.add_checksum(c_out)
                        appVariables.clientListFcn[i]['q_out'].put(c_out)
                    msg = "[sockets][/app-data/monitor-view] " + str(nodeId) + ": " + c_out
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                    break
            for i in range(len(appVariables.virtualNodeList)):
                if appVariables.virtualNodeList[i]['id'] == nodeId:
                    c_out = "error: queue full!"
                    if not appVariables.virtualNodeListFcn[i]['q_out'].full():
                        c_out = params['fback']
                        appVariables.virtualNodeListFcn[i]['q_out'].put(c_out)
                    msg = "[sockets][/app-data/monitor-view] " + c_out
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                    break
    return params

@sockets.route('/app-data/monitor-view')
def appdata_monitorview_socket(ws):
    counter_poll = 0
    n = 10
    count_retry = 0

    resp=False
    msg = "[sockets][/app-data/monitor-view] " + "open"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    if 'user' in session or not appVariables.appConfig['authentication']:
        if appVariables.clientList is not None:
            appVariables.clientList = sync_device_controls(appVariables.clientList)
        if appVariables.virtualNodeList is not None:
            appVariables.virtualNodeList = sync_device_controls(appVariables.virtualNodeList)

        msg = "[sockets][/app-data/monitor-view] " + "open2"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        while not ws.closed:
            message = ws.receive()
            params = None
            try:
                jsondata = json.loads(message)
                params = getcommands_appdata_monitorview(jsondata)
            except:
                appVariables.print_exception("[sockets][/app-data/monitor-view]")

            jsondata = getdata_appdata_monitorview(params,counter_poll)
            # print(jsondata)
            counter_poll = counter_poll + 1
            if not ws.closed:
                ws.send(json.dumps(jsondata))


    msg = "[sockets][/app-data/monitor-view] " + "close"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

@sockets.route('/app-data/monitor-sound')
def app_data_sound_socket(ws, enableDebugPrint=False):
    # app data inbox and outbox
    # for browser clients
    count = 0
    f_sampling=0
    audioData = None
    t_start = time.time()
    msg = "[sockets][/app-data/monitor-sound] " + "open"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    if 'user' in session or not appVariables.appConfig['authentication']:
        while not ws.closed:
            message = ws.receive()
            while True:
                gevent.sleep(0.01)
                t1 = time.time()
                dt = t1 - t_start

                if not appVariables.qAudioData.empty():
                    audioData = appVariables.qAudioData.get(block=False)
                else:
                    audioData = None

                if (audioData is not None) or (dt>=0.5):
                    t_start = t1
                    if dt>0:
                        f_sampling = f_sampling * 0.9 + (1/dt) * 0.1
                    else:
                        f_sampling = f_sampling * 0.9

                    if audioData is not None:
                        rawData = audioData['rawData']
                        rawFFT = audioData['fft']
                        fftString = audioData['fftString']
                    else:
                        rawData = []
                        rawFFT = []
                        fftString = ''

                    dt = datetime.datetime.now()
                    tm = str(dt.hour).zfill(2) + ":" + str(dt.minute).zfill(2) + ":" + str(dt.second).zfill(2)

                    info = '<span>' + str(count) + '&emsp; Server time: ' + tm + '&emsp; sampling rate: ' + str(int(f_sampling)) + ' Hz' + ' </span>'

                    jsondata = {
                        'time': tm,
                        'info': info,
                        'fftString': fftString,
                        'rawData': rawData,
                        'rawFFT': rawFFT,
                        'f_sampling': int(f_sampling)
                    }
                    count += 1
                    if count == 1000:
                        count = 0

                    if not ws.closed:
                        ws.send(json.dumps(jsondata))
                    break

    msg = "[sockets][/app-data/monitor-sound] " + "close"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

@sockets.route('/app-data/server-main')
def appdata_servermain_socket(ws):

    counter_poll = 0

    jsondata = {
        'info': 'no data',
        'connection':False,
    }
    debugInfo = ''
    temp=0
    cpu=0
    rec=False
    n_threads=0

    t0=time.time()

    msg = "[sockets][/app-data/server-main] " + "open"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    if 'user' in session or not appVariables.appConfig['authentication']:
        while not ws.closed:
            message = ws.receive()
            while True:
                gevent.sleep(0.01)
                dt = time.time() - t0
                if (dt >= 0.5) or appVariables.flags["new_server_data"] or (not appVariables.qDebug2.empty()):
                    t0 = time.time()
                    appVariables.flags["new_server_data"]=False
                    try:
                        jsondata = json.loads(message)
                    except:
                        appVariables.print_exception("[sockets][/app-data/server-main]")

                    counter_poll = counter_poll + 1
                    dt = datetime.datetime.now()
                    tm = str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)+":"+str(dt.second).zfill(2)

                    if appVariables.appConfig["rpi"]:
                        rec = appVariables.raspicam.isRecording()

                    if appVariables.queueServerStat.empty()==False:
                        ss=appVariables.queueServerStat.get(block=False)
                        temp=ss['temp']
                        cpu=ss['cpu']
                        n_threads=ss['n_threads']

                    info = '<span>' + str(counter_poll) + '&emsp;Server time: ' + tm + '&emsp;active threads: '+str(n_threads)+\
                           '</span>'

                    if appVariables.qDebug2.empty()==False:
                        debugInfo = appVariables.qDebug2.get()
                    else:
                        debugInfo=''

                    jsondata = {
                        'counter': counter_poll,
                        'info': info,
                        'temp': temp,
                        'cpu': cpu,
                        'rec': str(rec),
                        'debug': debugInfo
                    }

                    if not ws.closed:
                        ws.send(json.dumps(jsondata))

                    break

    msg = "[sockets][/app-data/server-main] " + "close"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)


def gen(camera):
    """Video streaming generator function."""
    # empty residual images
    if camera.has_frame():
        frame = camera.get_frame()

    while True:
        gevent.sleep(appVariables.frameInterval)
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_processed(camera):
    """Video streaming generator function."""
    # empty residual images
    if camera.has_processed_frame():
        frame = camera.get_processed_frame()

    while True:
        gevent.sleep(appVariables.frameInterval)
        frame = camera.get_processed_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_remote(camera,url):
    camera.stop()
    camera.set_url(url)
    camera.start()
    # empty residual images
    if camera.has_frame():
        frame = camera.get_frame()
    while True:
        gevent.sleep(appVariables.frameInterval)
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def jpeg_gen(camera):
    frame = camera.get_frame()
    yield frame

@app.route('/')
def mypisite():
    return render_template('index.html')


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"

    r.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


####      DATA general
@app.route('/api/video-feed')
def apiVideoFeed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if 'user' in session or not appVariables.appConfig['authentication']:
        return Response(gen(appVariables.raspicam),mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/video-feed/redirect',methods=['GET'])
def apiVideoFeedRedirect():
    cid = int(request.args.get('cid'))
    c_url=None
    if cid < len(appVariables.appSettings['cameras']):
        c_url = appVariables.appSettings['cameras'][cid]['url']
    if c_url is not None:
        return redirect(c_url, code=302)
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/video-feed/connected',methods=['GET'])
def apiVideoFeedConnected():
    cid = int(request.args.get('cid'))
    c_url=None
    if cid < len(appVariables.appSettings['cameras']):
        c_url = appVariables.appSettings['cameras'][cid]['url']
        # print(c_url)
        if (c_url is not None) and ('user' in session or not appVariables.appConfig['authentication']):
            return Response(gen_remote(appVariables.camera_remote,c_url),mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return jsonify({"error":"unauthorized access"})
    else:
        return jsonify({"error": "camera is not available"})




@app.route('/api/video-feed-processed')
def apiVideoFeedProcessed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if 'user' in session or not appVariables.appConfig['authentication']:
        if appVariables.appConfig['rpi'] == True:
            return Response(gen_processed(appVariables.raspicam),mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return Response(gen(appVariables.raspicam),mimetype='multipart/x-mixed-replace; boundary=frame')

    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/jpeg-feed')
def apiJpegFeed():
    if 'user' in session or not appVariables.appConfig['authentication']:
        def wsgi_app(environ, start_response):
            start_response('200 OK', [('Content-type','image/jpeg')])
            return jpeg_gen(appVariables.raspicam)
        return make_response(wsgi_app)
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/database/control-settings', methods=['GET','POST'])
def apiDatabaseControlSettings():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/control-settings]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                appVariables.userSettingsModel = appVariables.read_json_file('config/settings_model.json')
                sid = int(request.args.get('sensorId'))
                if appVariables.appConfig['mongo']:
                    if sid==-1:
                        query=None
                    else:
                        query={"sensorId":sid}
                    result = appVariables.mongomanager.find("mydb", "control_settings", query)
                    return json.dumps({"settingsModel":appVariables.userSettingsModel['control'],'data':result}, default=json_util.default)
            elif request.method == "POST":
                jsonstr = request.json
                param = jsonstr['param']
                if jsonstr['req'] == 1:
                    # update/insert
                    query1 = {
                        "sensorId": param['sensorId']
                    }

                    if '_id' in param:
                        del param['_id']

                    query2 = {"$set": param}

                    result_db = appVariables.mongomanager.update("mydb", "control_settings", query1, query2, ups=True)
                    msg = "[routes][/api/database/control-settings] " + str(result_db)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                elif jsonstr['req'] == 2:
                    # remove
                    query1 = {
                        "sensorId": param['sensorId']
                    }
                    result_db = appVariables.mongomanager.remove("mydb", "control_settings", query1)
                    msg = "[routes][/api/database/control-settings] " + str(result_db)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/control-settings]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/database/nodes',methods=['GET','POST'])
def apiDatabaseNodes():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/nodes]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                if appVariables.appConfig['mongo']:
                    result = appVariables.mongomanager.find("mydb", "sensors", None)
                    return json.dumps(result, default=json_util.default)
            elif request.method == "POST":
                jsonstr = request.json
                param = jsonstr['param']
                if jsonstr['req']==1:
                    # update
                    query1 = {
                        "s_id": param['s_id']
                    }
                    query2 = {
                        "$set":{
                            "info": param['info']
                        }
                    }
                    result_db = appVariables.mongomanager.update("mydb", "sensors", query1, query2, ups=True)
                    msg = "[routes][/api/database/nodes] " + str(result_db)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                if jsonstr['req']==2:
                    result_db = appVariables.mongomanager.remove("mydb", "sensors", {"s_id": param['s_id']})
                    msg = "[routes][/api/database/nodes] " + str(result_db)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/nodes]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/general/settings',methods=['GET','POST'])
def apiGeneralSettings():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/general/settings]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                return json.dumps(appVariables.appSettings)
            elif request.method == "POST":
                requestJson = request.json
                print(requestJson)
                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/settings]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return json.dumps({"error": "unauthorized access"})
@app.route('/api/database/settings', methods=['GET','POST'])
# @cross_origin(supports_credentials=True)
def apiDatabaseSettings():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/settings]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                user = request.args.get('username')

                if appVariables.appConfig['mongo']:
                    result = appVariables.mongomanager.find("mydb", "user_settings", {"username": user})
                    if len(result) > 0:
                        result = result[0]
                    else:
                        result = {}
                    return json.dumps({"settingsModel": appVariables.userSettingsModel, "userSettings": result,
                                       "nodeModelDB": appVariables.clientModelDB}, default=json_util.default)
            elif request.method == "POST":
                requestJson = request.json
                if appVariables.appConfig['mongo']:
                    user = requestJson['username']
                    jsondata = requestJson['settings']
                    query2 = {
                        "$set": {
                            jsondata["collection"]: jsondata["data"]
                        }
                    }
                    result_db = appVariables.mongomanager.update("mydb", "user_settings", {"username": user},query2,ups=True)
                    msg = "[routes][/api/database/settings] " + str(result_db)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/settings]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return json.dumps({"error":"unauthorized access"})

@app.route('/api/database/users',methods=['GET','POST'])
def apiDatabaseUsers():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/users]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                if appVariables.appConfig['mongo']:
                    result = appVariables.mongomanager.find("mydb", "users", None)
                    return json.dumps(result, default=json_util.default)
            if request.method == "POST":
                js = request.json
                if appVariables.appConfig['mongo']:
                    if js['req']==2:
                        # remove user
                        result_db = appVariables.mongomanager.remove("mydb", "users", {"username": js['username']})
                        msg = "[routes][/api/database/users] " + str(result_db)
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)
                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/users]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/database/user-info', methods=['GET', 'POST'])
def apiDatabaseUserInfo():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/user-info]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        if request.method == "GET":
            username = request.args.get('username')
            if appVariables.appConfig['mongo']:
                result = appVariables.mongomanager.find("mydb", "users", {"username":username})
                result=result[0]
                del result['password']
                return json.dumps(result, default=json_util.default)
        elif request.method == "POST":
            try:
                js = request.json
                if js['newPassword'] != js['confirmPassword']:
                    result = appVariables.const1["RESULT_FAIL"]
                    return json.dumps({"result": result})
                else:
                    if appVariables.appConfig['mongo']:
                        # update user info only if username and password matches the record in the database
                        query2 = {
                            "$set":{
                                "email":js["email"],
                                "password": js["newPassword"],
                                "active": 1
                            }
                        }
                        result_db = appVariables.mongomanager.update("mydb", "users", {"username": js['username'],"password": js['password']}, query2, ups=False)
                        msg = "[routes][/api/database/user-info] " + str(result_db)
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)
                    if (result_db['updatedExisting']):
                        result = appVariables.const1["RESULT_OK"]
                    else:
                        result = appVariables.const1["RESULT_FAIL"]
                    return json.dumps({"result": result})
            except:
                appVariables.print_exception("[routes][/api/database/user-info]")
                result = appVariables.const1["RESULT_FAIL"]

            return jsonify({"result": result})
    else:
        return jsonify({"error": "unauthorized access"})

@app.route('/api/database/sensors/delete',methods=['GET','POST'])
def apiDatabaseSensorsDelete():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/sensors/delete]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
            
        js = request.json
        datenow = datetime.datetime.now()
        dt = datetime.timedelta(days=js['value'])
        date1 = datenow-dt

        query1 = {
            "ts":{"$lt":str(date1)}
        }
        result_db = appVariables.mongomanager.remove("mydb", "sensor_data", query1)
        msg = "[routes][/api/database/sensors/delete] " + str(result_db)
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/database/sensors/nlast')
def apiDatabaseSensorsNlast():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/sensors/nlast]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            param = request.args.get('param')
            param = json.loads(param)
            sid = param['sensorId']
            cid = param['channelId']
            N = param['n']
            if appVariables.appConfig['mongo']:
                # result = appVariables.mongomanager.find("mydb","sensor_data",{"s_id":sid,"s_chan":cid})
                result = appVariables.mongomanager.find_last_records("mydb", "sensor_data", {"s_id": sid, "s_chan": cid},N)
                return json.dumps(result, default=json_util.default)
        except:
            appVariables.print_exception("[routes][/api/database/sensors/nlast]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/database/sensors/last')
def apiDatabaseSensorsLast():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/sensors/last]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            param = request.args.get('param')
            param = json.loads(param)
            sid = param['sensorId']
            cid = param['channelId']
            date1 = datetime.datetime.now()
            startdate = date1 - datetime.timedelta(hours=param['h'])
            # "2017-02-19 14:12:42.979000"
            if appVariables.appConfig['mongo']:
                query={"s_id": sid,
                       "s_chan": cid,
                       "ts": { "$gt": str(startdate) }
                       }
                # result = appVariables.mongomanager.find("mydb","sensor_data",{"s_id":sid,"s_chan":cid})
                result = appVariables.mongomanager.find_last_records("mydb", "sensor_data", query, 0)
                return json.dumps(result, default=json_util.default)
        except:
            appVariables.print_exception("[routes][/api/database/sensors/last]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/database/control', methods = ['GET','POST'])
def apiDatabaseControl():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/database/control]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            if request.method == "GET":
                sid = request.args.get('s_id')
                n = request.args.get('n')
                # param = request.args.get('params')
                # param = json.loads(param)
                # sid = param['s_id']
                # n = param['n']
                sid=int(sid)
                n=int(n)

                # sid = int(sid)
                # n = int(n)
                if appVariables.appConfig['mongo']:
                    # result = appVariables.mongomanager.find("mydb","control_data",{"s_id":sid})
                    # return json.dumps(result, default=json_util.default)
                    result = appVariables.mongomanager.find_last_records("mydb", "control_data", {"s_id": sid}, n)
                    return json.dumps(result, default=json_util.default)
            else:
                jdata=request.json
                print jdata
                # if (req == 1):
                #     # remove selected
                #     appVariables.qDatabaseIn.put(("/api/database/control","DELETE FROM Control WHERE ID = (?) AND SensorId = (?) " ,(rowid,sid)))
                # if (req == 2):
                #     # remove range
                #     appVariables.qDatabaseIn.put(("/api/database/control","DELETE FROM Control WHERE\
                #                         ID BETWEEN (?) AND (?) AND SensorId = (?) " ,(row1,row2,sid)))
                # if (req == 3):
                #     # remove all
                #     appVariables.qDatabaseIn.put(("/api/database/control","DELETE FROM Control WHERE SensorId = (?)",(sid,)))
                if jdata['req']==1:
                    # remove latest samples
                    pass
                    # data = request_db((request.remote_addr+"/api/database/control","DELETE FROM Control WHERE ID IN (SELECT ID FROM Control WHERE SensorId = (?) ORDER BY Timestamp DESC LIMIT " + str(jdata['n']) + ")" ,(jdata['sid'],)))

                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
        except:
            appVariables.print_exception("[routes][/api/database/control]")
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


####      DATA routes (ws)
@app.route('/api/ws/program', methods=['GET','POST'])
def apiWsProgram():
    count_retry = 0
    data = False
    retdata = {'result': 'NODATA'}
    if 'user' in session or not appVariables.appConfig['authentication']:

        msg = "[routes][/api/ws/program]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        if request.method == "GET":

            cmd = appVariables.systemSettings['codeTable']['CMD_GET_PROGRAM']
            cmdcode = cmd['cmd']

            cmd_string = str(cmdcode)

            if not appVariables.wsOutQueue.full():
                appVariables.wsOutQueue.put(cmd_string)

            while True:
                t0 = time.time()
                while time.time() - t0 < 3:
                    time.sleep(0.01)
                    if not appVariables.queue_ws_app_data.empty():
                        data = appVariables.queue_ws_app_data.get(block=False)
                        if data != False:
                            break

                try:
                    retry=False
                    if data != False:
                        str1 = data
                        string = str1
                        stringArray = string.split(",")
                        msg = "[routes][/api/ws/program] " + string
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)

                        a = [0] * len(stringArray)
                        for i in range(len(stringArray)):
                            try:
                                a[i] = int(stringArray[i])
                            except:
                                a[i] = 0

                        if a[0] == cmdcode:
                            n = a[4]
                            arr = [{'index':index,'dist':a[5+index],'time':a[5+n+index]} for index in range(n)]
                            retdata = {'program':arr,
                                    'interval':{'h':a[1],'m':a[2],'s':a[3]}
                                    }
                            break
                        else:
                            retry=True
                    if retry:
                        if not appVariables.wsOutQueue.full():
                            appVariables.wsOutQueue.put(cmd_string)
                        count_retry = count_retry + 1
                        if count_retry >= appVariables.MAX_COM_RETRY:
                            result = appVariables.const1["RESULT_FAIL"]
                            return json.dumps({"result": result})
                except:
                    appVariables.print_exception("[routes][/api/ws/program]")
                    if not appVariables.wsOutQueue.full():
                        appVariables.wsOutQueue.put(cmd_string)
                    count_retry = count_retry + 1
                    if count_retry >= appVariables.MAX_COM_RETRY:
                        result = appVariables.const1["RESULT_FAIL"]
                        return json.dumps({"result": result})

            return json.dumps(retdata)

        elif request.method == "POST":
            cmd = appVariables.systemSettings['codeTable']['CMD_SET_PROGRAM']
            cmdcode = cmd['cmd']

            a = []
            for i in range(4):
                a.append(0)

            n = len(request.json['program'])
            for i in range(2 * n + 1):
                a.append(0)

            interval = request.json['interval']
            a[0] = interval['h']
            a[1] = interval['m']
            a[2] = interval['s']
            a[3] = n
            #write eeprom
            a[4] = 1
            i = 4

            for element in request.json['program']:
                a[i + 1] = element['dist']
                a[i + 1 + n] = element['time']
                i = i + 1

            csv = "".join([str(el)+',' for el in a])
            csv = csv[:-1]
            msg = "[routes][/api/ws/program] " + csv
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

            cmd_string = str(cmdcode) + ','+csv

            if not appVariables.wsOutQueue.full():
                appVariables.wsOutQueue.put(cmd_string)

            result = appVariables.const1["RESULT_OK"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/ws/setup', methods=['GET','POST'])
def apiWsSetup():
    count = 0
    count_retry = 0
    data = False
    retdata = {'result': 'NODATA'}
    if 'user' in session or not appVariables.appConfig['authentication']:

        msg = "[routes][/api/ws/setup]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        if request.method == 'GET':
            cmd = appVariables.systemSettings['codeTable']['CMD_GET_SETTINGS']
            cmdcode = cmd['cmd']
            cmd_string = str(cmdcode)
            retdata = {
                'mode':1,
               'maxpump':220,
               'Kp':1,
               'Ki':0,
               'Kd':0
            }

            if not appVariables.wsOutQueue.full():
                appVariables.wsOutQueue.put(cmd_string)
            try:
                while True:
                    t0 = time.time()
                    while time.time() - t0 < 3:
                        time.sleep(0.01)
                        if not appVariables.queue_ws_app_data.empty():
                            data = appVariables.queue_ws_app_data.get(block=False)
                            if data != False:
                                break
                    try:
                        retry=False
                        if data!=False:
                            str1 = data
                            string = str1
                            stringArray = string.split(",")
                            msg = "[routes][/api/ws/setup] " + string
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)
                            a = [0] * len(stringArray)
                            for i in range(len(stringArray)):
                                try:
                                    a[i] = int(stringArray[i])
                                except:
                                    a[i] = 0

                            if a[0] == cmdcode:
                                retdata['mode']=a[1]
                                retdata['maxpump']=a[2]
                                retdata['Kp']=a[3]*0.001
                                retdata['Ki']=a[4]*0.001
                                retdata['Kd']=a[5]*0.001
                                break
                            else:
                                retry=True

                        if retry:
                            if not appVariables.wsOutQueue.full():
                                appVariables.wsOutQueue.put(cmd_string)
                            count_retry = count_retry + 1
                            if count_retry >= appVariables.MAX_COM_RETRY:
                                result = appVariables.const1["RESULT_FAIL"]
                                return json.dumps({"result": result})
                    except:
                        appVariables.print_exception("[routes][/api/ws/setup]")
                        if not appVariables.wsOutQueue.full():
                            appVariables.wsOutQueue.put(cmd_string)
                        count_retry = count_retry + 1
                        if count_retry >= appVariables.MAX_COM_RETRY:
                            result = appVariables.const1["RESULT_FAIL"]
                            return json.dumps({"result": result})
            except:
                appVariables.print_exception("[routes][/api/ws/setup]")
                result = appVariables.const1["RESULT_FAIL"]
                return json.dumps({"result": result})

            return json.dumps(retdata)
        if request.method == 'POST':
            result = appVariables.const1["RESULT_OK"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/ws/setup/sync-time', methods=['POST'])
def apiWsSetupSyncTime():
    if 'user' in session or not appVariables.appConfig['authentication']:

        msg = "[routes][/api/ws/setup/sync-time]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        cmd = appVariables.systemSettings['codeTable']['CMD_SET_TIME']
        cmdcode = cmd['cmd']

        dt = datetime.datetime.now()
        body = str(dt.hour)+","+str(dt.minute)+","+str(dt.second)
        cmd_string = str(cmdcode) + ',' + body
        if not appVariables.wsOutQueue.full():
            appVariables.wsOutQueue.put(cmd_string)

        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

####      DATA routes


@app.route('/api/ws/control-step', methods=['GET'])
def apiWsControlStep():
    if 'user' in session or not appVariables.appConfig['authentication']:
        msg = "[routes][/api/ws/control-step]"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        if request.method == "GET":
            appVariables.flag_sim['control']=True
            result = appVariables.const1["RESULT_OK"]
            return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/model/nodes', methods=['GET'])
def apiModelNodes():
    if 'user' in session or not appVariables.appConfig['authentication']:
        if request.method == "GET":
            return jsonify({"nodeModelDB": appVariables.clientModelDB})
    else:
        return jsonify({"error":"unauthorized access"})


#### DOWNLOAD FILES
@app.route('/api/download/log', methods=['GET'])
def apiDownloadLog():
    if 'user' in session or not appVariables.appConfig['authentication']:
        filename = "log.txt"
        return send_file('user_data/' + filename,
                         mimetype='text/plain',
                         attachment_filename=filename,
                         as_attachment=True)
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/download/log-dbg', methods=['GET'])
def apiDownloadLogDbg():
    if 'user' in session or not appVariables.appConfig['authentication']:
        filename = appVariables.appConfig["log_file_stdout"]
        return send_file(filename,
                         mimetype='text/plain',
                         attachment_filename="log_file_stdout",
                         as_attachment=True)
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/download/log-tcp-in', methods=['GET'])
def apiDownloadLogTcpIn():
    if 'user' in session or not appVariables.appConfig['authentication']:
        filename = appVariables.appConfig["log_file_tcp_in"]
        return send_file(filename,
                         mimetype='text/plain',
                         attachment_filename="log_file_tcp_in",
                         as_attachment=True)
    else:
        return jsonify({"error": "unauthorized access"})

@app.route('/api/download/log-tcp-out', methods=['GET'])
def apiDownloadLogTcpOut():
    if 'user' in session or not appVariables.appConfig['authentication']:
        filename = appVariables.appConfig["log_file_tcp_out"]
        return send_file(filename,
                         mimetype='text/plain',
                         attachment_filename="log_file_tcp_out",
                         as_attachment=True)
    else:
        return jsonify({"error": "unauthorized access"})

####      API
@app.route('/api/start-rec')
def apiStartRec():
    if 'user' in session or not appVariables.appConfig['authentication']:
        appVariables.raspicam.start_recording()
        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/stop-rec')
def apiStopRec():
    if 'user' in session or not appVariables.appConfig['authentication']:
        appVariables.raspicam.stop_recording()
        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/restart')
def apiRestart():
    if 'user' in session or not appVariables.appConfig['authentication']:
        try:
            # open process, DON'T wait for result (stdin,stdout,stderr are None)
            proc = subprocess.Popen(['bash '+appVariables.appConfig["restart_script"]], shell=True,
                         stdin=None, stdout=None, stderr=None, close_fds=True)
            result = appVariables.const1["RESULT_OK"]
            return json.dumps({"result": result})
            # restart_program()
        except:
            appVariables.print_exception("[routes][/api/restart]")
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/reboot')
def apiReboot():
    if 'user' in session or not appVariables.appConfig['authentication']:
        try:
            server_cmd.restart()
            result = appVariables.const1["RESULT_OK"]
        except:
            appVariables.print_exception("[routes][/api/reboot]")
            result = appVariables.const1["RESULT_FAIL"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})
        
@app.route('/api/start-sound-a')
def apiStartSoundA():
    if 'user' in session or not appVariables.appConfig['authentication']:
        appVariables.audio_a1.start()
        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})

@app.route('/api/stop-sound-a')
def apiStopSoundA():
    if 'user' in session or not appVariables.appConfig['authentication']:
        appVariables.audio_a1.stop()
        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/bluetooth-serial/send', methods=['POST'])
def apiBluetoothSerial():
    if 'user' in session or not appVariables.appConfig['authentication']:
        json_data = request.json
        cmdText = json_data['cmd']
        body = json_data['data']

        cmd = appVariables.systemSettings['codeTable'][cmdText]
        cmdcode = cmd['cmd']
        cmd_string = str(cmdcode)+','+body

        msg = "[routes][/api/bluetooth-serial/send] " + cmd_string
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        if not appVariables.wsOutQueue.full():
            appVariables.wsOutQueue.put(cmd_string)

        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        return jsonify({"error":"unauthorized access"})


@app.route('/api/isloggedin', methods=['GET'])
# @login_required
# @cross_origin(supports_credentials=True)
def apiIsLoggedIn():
    msg = "[routes][/api/isloggedin]"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    if 'user' in session or not appVariables.appConfig['authentication']:
        result = appVariables.const1["RESULT_OK"]
        return json.dumps({"result": result})
    else:
        result = appVariables.const1["RESULT_FAIL"]
        return json.dumps({"result": result})

@app.route('/api/login', methods=['POST'])
# @cross_origin(supports_credentials=True)
def apiLogin():
    json_data = request.json
    msg = "[routes][/api/login]" + " user: " + json_data['username']
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    try:
        if appVariables.appConfig['mongo']:
            result = appVariables.mongomanager.find("mydb", "users", {"username": json_data['username'], "password": json_data['password']})
            if len(result) > 0:
                session['user'] = True
                session.permanent = False
                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
            else:
                result = appVariables.const1["RESULT_FAIL"]
                return json.dumps({"result": result})
    except:
        appVariables.print_exception("[routes][/api/login]")
        result = appVariables.const1["RESULT_FAIL"]
        return json.dumps({"result": result})

@app.route('/api/logout', methods=['GET'])
def apiLogout(debug = False):
    msg = "[routes][/api/logout]"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    session.pop('user', None)
    result = appVariables.const1["RESULT_OK"]
    return json.dumps({"result": result})

@app.route('/api/register', methods=['POST'])
def apiRegister():
    result=1
    js = request.json

    generatedPassword = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    msg = "[routes][/api/register] " + generatedPassword
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    # me == the sender's email address
    # you == the recipient's email address

    mlist = [line.rstrip() for line in open('app_data/mail.txt','r')]

    mail_user = mlist[0]
    mail_pwd = mlist[1]
    FROM = mlist[2]
    admin = mlist[3]
    smtp = mlist[4]
    smtp_port = int(mlist[5])

    msg = "[routes][/api/register] " + mail_user+','+mail_pwd+','+FROM+','+admin+','+smtp+','+str(smtp_port)
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    TO = js['email']
    msg = MIMEText("You have requested a registration for SmartHome Web App. Your user name is " +
                   js['username'] + " and your temporary password is " + generatedPassword +
                   "\r\nUse this password to log in. You can change it later.")

    msg['Subject'] = 'SmartHome registration for ' + js['username']
    msg['From'] = FROM
    msg['To'] = TO
    msg['Cc'] = admin
    cc = [admin]
    toaddrs = [TO] + cc

    if appVariables.appConfig['mongo']:
        result = appVariables.mongomanager.find("mydb", "users",
                                                {"username": js['username']})
        if len(result)>0:
            # user already in the database
            result = appVariables.const1["RESULT_FAIL"]
            return json.dumps({"result": result})
        else:
            # send mail with temporary password
            try:
                server = smtplib.SMTP(smtp, smtp_port)
                ##        server.ehlo()
                server.set_debuglevel(True)
                server.starttls()
                server.login(mail_user, mail_pwd)
                server.sendmail(FROM, toaddrs, msg.as_string())
                server.close()
                msg = "[routes][/api/register] " + 'mail sent'
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)
                # insert user
                result_db = appVariables.mongomanager.insert("mydb", "users",
                                                 {"username": js['username'], "password": generatedPassword,
                                                  "email": js['email'], "active": 0})
                msg = "[routes][/api/register] " + str(result_db)
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)
                result = appVariables.const1["RESULT_OK"]
                return json.dumps({"result": result})
            except:
                appVariables.print_exception("[routes][/api/register]")
                result = appVariables.const1["RESULT_FAIL"]
                return json.dumps({"result": result})




# unsecured api (used for testing)
@app.route('/api/test/control', methods=['GET'])
def apiTestControl():
    msg = "[routes][/api/test/control]"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)
    appVariables.flag_sim['control']=True
    result = appVariables.const1["RESULT_OK"]
    return json.dumps({"result": result})



# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    q_read_tcp = Queue(maxsize=10)
    q_write_tcp = Queue(maxsize=10)
    time.sleep(1)

    if appVariables.appConfig['modules']['watering_system']:
        thread1 = IrrigationControlThread()
        thread1.start()

    thread2 = DataBucketThread()
    thread2.start()

    # if appVariables.appConfig['rpi']:
    #     thread3 = TCPServerThread(q_read=q_read_tcp,q_write=q_write_tcp)
    #     thread3.start()
    # if appVariables.appConfig['modules']['tcp_server']:
    #     thread3 = TCPServerThread(q_read=q_read_tcp, q_write=q_write_tcp)
    #     thread3.start()
    if appVariables.appConfig['modules']['tcp_server']:
        t = threading.Thread(target=simple_tcp_server)
        t.daemon = True
        t.start()

    thread5 = DebugPrintThread()
    thread5.start()

    thread6 = ServerStatusThread()
    thread6.start()



    thread8 = ControlSystemsThread()
    thread8.start()

    if appVariables.appConfig['rpi']:
        appVariables.camera_remote = Camera2(None, appVariables.qDebug1)
        if appVariables.appConfig['modules']['sound']:
            appVariables.audio_a1 = audioAnalyzer()
            thread7 = SoundDataThread()
            thread7.start()
        if appVariables.appConfig['modules']['pi_camera']:
            appVariables.raspicam = Camera1(640, 480, appVariables.qDebug1)
        else:
            appVariables.raspicam = Camera1()



    p = Process(target=DatabaseManagerProcess, args=(appVariables.qDatabaseIn,appVariables.qDatabaseOut,appVariables.qDebug1,appVariables.appConfig['db_file']))
    p.start()

    msg = "[main] " + 'server started'
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()



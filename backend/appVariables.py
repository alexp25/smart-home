import json
from multiprocessing import Queue
import sys

def print_exception(msg):
    exc_type, exc_value = sys.exc_info()[:2]
    exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
    em1 = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
    msg1 = msg + ' ' + em1 + ', ' + exceptionMessage
    if not qDebug1.full():
        qDebug1.put(msg1)

def read_json_file(fname):
    jsondata = None
    with open(fname) as f:
        file_contents = f.read()
    try:
        jsondata = json.loads(file_contents)
    except:
        print_exception("read json file "+fname)

    return jsondata

def add_checksum(msg):
    msg1 = msg.split(",")
    msgdata = [0] * len(msg1)
    chksum=0
    for i in range(len(msg1)):
        msgdata[i] = int(msg1[i])
        chksum += msgdata[i]
    msg2 = str(msg) + ',' + str(chksum)

    if(msgdata[0] not in [1,100,211]):
        msginfo = "[add_checksum] " + msg2
        if not qDebug1.full():
            qDebug1.put(msginfo)

    return msg2

def init():
    global myList
    myList = []
    global flags,server_commands_default,server_commands,server_params,server_status
    global deviceCmdCodes,clientModelFcn,clientModel,clientList,clientListFcn,clientModelDB
    global clientInfoList,virtualNodeInfoList
    global virtualNodeModelFcn,virtualNodeList,virtualNodeListFcn
    global appConfig

    global qDebug1,qDebug2,queue_ws_app_data,queue_ws_control,wsOutQueue,queueServerStat,qAudioData,qAudioData2,qDatabaseIn,qDatabaseOut
    global raspicam
    global audio_a1
    global serverstat

    global systemSettings

    global MAX_COM_RETRY
    global db_timeout
    global frameInterval

    global userSettingsModel,appSettings

    global mongomanager

    global const1

    global flag_sim

    global qTCPIn, qTCPOut

    global camera_remote

    flag_sim={
        'control':False
    }

    const1 = {
        "RESULT_OK":0,
        "RESULT_FAIL":1
    }

    db_timeout=10.0
    raspicam=None
    camera_remote=None

    frameInterval = 0.1
    MAX_COM_RETRY = 25
    wsdata = {'program': [{'index': 0, 'dist': 10, 'time': 10},
                        {'index': 1, 'dist': 20, 'time': 10},
                        {'index': 2, 'dist': 30, 'time': 10},
                        {'index': 3, 'dist': 40, 'time': 10}
                        ],
            'interval': {'h': 12, 'm': 0, 's': 10}
            }
    wscodes = {'CMD_SET_MODE_AUTO': {'cmd': 102, 'body': False},
             'CMD_SET_MODE_MANUAL': {'cmd': 101, 'body': False},
             'CMD_SET_MODE_TEST': {'cmd': 103, 'body': False},

             'CMD_SET_CMD_PUMP': {'cmd': 111, 'body': True},
             'CMD_SET_CMD_CARR': {'cmd': 112, 'body': True},
             'CMD_START_PROGRAM': {'cmd': 113, 'body': False},
             'CMD_STOP_PROGRAM': {'cmd': 114, 'body': False},
             'CMD_CARR_RET': {'cmd': 115, 'body': False},
             'CMD_NEXT_PLANT': {'cmd': 116, 'body': False},

             'CMD_SET_REF_CARR': {'cmd': 121, 'body': True},

             'CMD_SET_COUNTD_RST': {'cmd': 131, 'body': False},
             'CMD_SET_COUNTD_UPD': {'cmd': 132, 'body': True},
             'CMD_SET_TIME': {'cmd': 133, 'body': True},

             'CMD_SET_PROGRAM': {'cmd': 141, 'body': True},
             'CMD_SET_OTHER': {'cmd': 142, 'body': True},
             'CMD_SET_PLANT_WTIME': {'cmd': 143, 'body': True},

             'CMD_START_VISUAL_INSPECTION': {'cmd': 161, 'body': False},
             'CMD_STOP_VISUAL_INSPECTION': {'cmd': 162, 'body': False},
             'CMD_MOVE_NEXT': {'cmd': 163, 'body': False},

             'CMD_SET_DEFAULT_PROGRAM': {'cmd': 191, 'body': False},

             'CMD_GET_STATUS': {'cmd': 211, 'body': False},
             'CMD_GET_SETTINGS': {'cmd': 212, 'body': False},
             'CMD_GET_PROGRAM': {'cmd': 221, 'body': False},

             'CMD_GET_PLANT_WTIME': {'cmd': 243, 'body': True},

             }

    systemSettings = {'wateringSystemSettings': wsdata, 'codeTable': wscodes, 'updateRate': 1}




    # debug queue (print, tcp debugging)
    qDebug1 = Queue(maxsize=50)
    qDebug2 = Queue(maxsize=50)
    QSIZE = 5
    QSIZE2 = 1
    # websocket data
    queue_ws_app_data = Queue(maxsize=QSIZE)
    # thread data
    queue_ws_control = Queue(maxsize=QSIZE)
    # watering system out queue
    wsOutQueue = Queue(maxsize=QSIZE)

    # server status queue
    queueServerStat = Queue(maxsize=2)
    # audio data
    qAudioData = Queue(maxsize=5)
    qAudioData2 = Queue(maxsize=1)
    # database
    qDatabaseIn = Queue(maxsize=10)
    qDatabaseOut = Queue()

    # tcp data (for logging)
    qTCPIn = Queue(maxsize=50)
    qTCPOut = Queue(maxsize=50)

    appConfig = read_json_file('config/server/config.json')
    userSettingsModel = read_json_file('config/settings_model.json')
    appSettings = read_json_file('config/app_settings.json')

    flags = {
        "new_client_data": False,
        "new_server_data": False
    }
    server_commands_default = {'spab': False, 'log': False}
    server_commands = {'spab': False, 'log': False}
    server_params = {'spab_um': 50, 'spab_du': 10, 'selected_node': 0}
    server_status = {'spab_gen': (0, 0)}

    deviceCmdCodes = {'request_data_def': 100, 'request_cmd_def': 101}
    clientModelFcn = {
        'discovered': False,
        'connection': None,
        'prev_id': 0,
        'q_in': None,
        'q_out': None,
        't0': None,
        't0_polling': None,
        't0_log': None
    }
    clientModel = {
        'id': 0,
        'ip': '',
        'data': [],
        'sdata': False,
        'commands': False,
        'settings': False,
        'type': 0,
        'counter_rx': 0,
        'counter_tx': 0
    }
    clientList = []
    clientListFcn = []
    clientModelDB = []
    clientInfoList = []

    virtualNodeModelFcn = {
        'q_out': None
    }
    virtualNodeList = []
    virtualNodeListFcn = []

    virtualNodeInfoList = []
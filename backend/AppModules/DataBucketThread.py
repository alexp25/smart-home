import time
import appVariables
import datetime
from threading import Thread
import sys
import json
import copy

class DataBucketThread(Thread):
    def run(self):
        t0=time.time()
        t0_ws=t0
        t02=t0

        flag1=False
        flag5=False

        # print(appVariables.myList)
        msg = "[DataBucketThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        # this thread gathers data from other modules and dispatches to control threads
        while True:
            try:
                time.sleep(0.01)

                # get data from video processing
                if appVariables.appConfig['rpi']:
                    if appVariables.raspicam is not None:
                        video_processing_result = appVariables.raspicam.get_processing_result()
                        if video_processing_result is not None:
                            msg="[DataBucketThread] " + "video processing: " + json.dumps(video_processing_result)
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)

                # get data from nodes and prepare for display
                t1 = time.time()
                # request data from nodes (polling), each with own sampling rate


                if t1 - t0 >= 5:
                    t0 = t1
                    flag5=True

                if t1 - t02 >= 1:
                    t02 = t1
                    flag1=True

                for i in range(len(appVariables.clientList)):
                    dt_poll = 1
                    # request data only from discovered clients
                    if appVariables.clientList[i]['id']!=0 and appVariables.clientList[i]['sdata']!=False:
                        if 'settings' in appVariables.clientList[i]:
                            dt_poll=appVariables.clientList[i]['settings']['polling']

                    if (t1-appVariables.clientListFcn[i]['t0_polling'])>=dt_poll:
                        appVariables.clientListFcn[i]['t0_polling']=t1
                        if not appVariables.clientListFcn[i]['q_out'].full():
                            appVariables.clientListFcn[i]['q_out'].put("211")
                    # equivalent of dhcp discover, send discover message to connected clients
                    # the clients should return basic info
                    if flag5 or (appVariables.clientList[i]['id']==0 and flag1):
                        # msg = "[DataBucketThread] " + "code 100: " + str(appVariables.clientList[i]['id'])
                        # if not appVariables.qDebug1.full():
                        #     appVariables.qDebug1.put(msg)
                        if not appVariables.clientListFcn[i]['q_out'].full():
                            appVariables.clientListFcn[i]['q_out'].put("100")

                    # update client with metadata, when client is identified or when client id is changed
                    if appVariables.clientList[i]['id'] != appVariables.clientListFcn[i]['prev_id']:
                        appVariables.clientListFcn[i]['prev_id'] = appVariables.clientList[i]['id']
                        # get metadata from client model, update client
                        msg = "[DataBucketThread] " + "update client model: " + str(appVariables.clientList[i]['id'])
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)

                        for j in range(len(appVariables.clientModelDB)):
                            if appVariables.clientModelDB[j]['id'] == appVariables.clientList[i]['type']:
                                appVariables.clientList[i]['sdata'] = copy.deepcopy(
                                    appVariables.clientModelDB[j]['configuration']['metadata'])
                                appVariables.clientList[i]['commands'] = copy.deepcopy(
                                    appVariables.clientModelDB[j]['configuration']['commands'])
                                appVariables.clientList[i]['settings'] = copy.deepcopy(
                                    appVariables.clientModelDB[j]['configuration']['communication'])
                                appVariables.clientList[i]['info'] = {
                                    'type': appVariables.clientModelDB[j]['type'],
                                    'class': appVariables.clientModelDB[j]['class']
                                }
                                break

                # basic i/o client operations
                for i in range(len(appVariables.clientList)):
                    # send data to app controlled clients
                    # [watering system]
                    if appVariables.clientList[i]['type'] == 201:
                        if not appVariables.wsOutQueue.empty():
                            cmd_string = appVariables.wsOutQueue.get(block=False)
                            msg = "[DataBucketThread] " + "ws out: " + cmd_string
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)
                            if not appVariables.clientListFcn[i]['q_out'].full():
                                appVariables.clientListFcn[i]['q_out'].put(cmd_string)

                    # [sound lights]
                    # handle sound data (for led arrays)
                    if appVariables.clientList[i]['type'] == 102:
                        if not appVariables.qAudioData2.empty():
                            soundData = appVariables.qAudioData2.get(block=False)
                            if soundData['fftString'] is not None:
                                new_data = '1,' + soundData['fftString']
                                if not appVariables.clientListFcn[i]['q_out'].full():
                                    appVariables.clientListFcn[i]['q_out'].put(new_data)

                    # retrieve and process data from clients
                    if not appVariables.clientListFcn[i]['q_in'].empty():
                        cdata = appVariables.clientListFcn[i]['q_in'].get(block=False)
                        # print(cdata)
                        # update client with structured data (fill in metadata)
                        if cdata is not None:
                            if cdata['data'][0] == 211 and appVariables.clientList[i]['sdata'] != False:
                                len_mdata = len(appVariables.clientList[i]['sdata'])
                                for j in range(len(cdata['data']) - 1):
                                    if j < len_mdata:
                                        appVariables.clientList[i]['sdata'][j]['value'] = cdata['data'][appVariables.clientList[i]['sdata'][j]['pos']]
                                appVariables.flags["new_client_data"] = True
                        # retrieve data for special clients (app controlled)
                        if appVariables.clientList[i]['type'] == 201:
                            if not appVariables.queue_ws_app_data.full():
                                appVariables.queue_ws_app_data.put(cdata['str'])
                            if not appVariables.queue_ws_control.full():
                                appVariables.queue_ws_control.put(cdata['str'])

                        if cdata is not None and appVariables.clientList[i]['sdata'] != False:
                            # write data to database (log)
                            datatypes = appVariables.clientList[i]['sdata']
                            has_logged = False
                            for k in range(len(datatypes)):
                                if k < len(cdata['data']):
                                    if 'log' in datatypes[k]:
                                        dt_log = datatypes[k]['log']
                                        if (dt_log != 0) and (t1 - appVariables.clientListFcn[i]['t0_log'] >= dt_log):
                                            has_logged = True
                                            cid = datatypes[k]['id']
                                            pos = datatypes[k]['pos']
                                            timestamp = datetime.datetime.now()
                                            msg = "[DataBucketThread] " + "db log" + ', id: ' + str(
                                                appVariables.clientList[i]['id']) + ', cid: ' + str(cid)
                                            if not appVariables.qDebug1.full():
                                                appVariables.qDebug1.put(msg)

                                            if appVariables.appConfig['mongo']:
                                                doc = {
                                                    "s_id":appVariables.clientList[i]['id'],
                                                    "s_type":appVariables.clientList[i]['type'],
                                                    "s_chan":cid,
                                                    "ts": str(timestamp),
                                                    "value": cdata['data'][pos]
                                                }
                                                appVariables.mongomanager.insert("mydb","sensor_data",doc)

                                                # add sensor to database or update sensor info
                                                query1 = {
                                                    "s_id":appVariables.clientList[i]['id']
                                                }
                                                query2 = {
                                                    "$set":{
                                                        "s_id":appVariables.clientList[i]['id'],
                                                        "s_type":appVariables.clientList[i]['type'],
                                                        # "n_chan":len(cdata['data'])
                                                        "n_chan": len(datatypes)
                                                    }
                                                }
                                                appVariables.mongomanager.update("mydb", "sensors", query1, query2, ups=True)
                                else:
                                    break
                            if has_logged:
                                appVariables.clientListFcn[i]['t0_log'] = t1
                            break

                flag1 = False
                flag5 = False

            except:
                exc_type, exc_value = sys.exc_info()[:2]
                exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
                crt_time = datetime.datetime.now().strftime("%H:%M:%S.%f")
                msg = "[DataBucketThread] " + exceptionMessage
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)
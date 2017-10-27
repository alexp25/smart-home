import time
import appVariables
from threading import Thread
import sys
import json
import datetime
from bson import json_util


def spab_to_cmd(spab,um,du):
    if spab == 1:
        return um + du
    elif spab == 0:
        return um - du

class IrrigationControlThread(Thread):
    ##   thread for data analysis and control algorithms
    def __init__(self):
        Thread.__init__(self)


        self.Ts = 86400.0
        self.Ts = appVariables.appConfig['ws_ts'] * 3600
        self.q0=[]
        self.q1=[]
        self.q2=[]
        self.params=[]

    def loadControlSettings(self):
        data=['']
        if appVariables.appConfig['mongo']:
            data = appVariables.mongomanager.find("mydb", "control_settings", None)
        if len(data) > 0:
            self.params = data
            self.ctrlSettings=[]
    
            # self.q0 = [0] * len(self.params)
            # self.q1 = [0] * len(self.params)
            # self.q2 = [0] * len(self.params)

            msg = "[IrrigationControlThread] " + "Ts: " + str(self.Ts)
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

            msg = "[IrrigationControlThread] " + "settings loaded: " + json.dumps(data, default=json_util.default)
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)


            for i in range(len(self.params)):
                js = self.params[i] 
                Kp = js['Kp']
                Ki = js['Ki']
                Kd = js['Kd']
                q0 = Kp + self.Ts * Ki + Kd / self.Ts
                q1 = - Kp - 2 * Kd / self.Ts
                q2 = Kd / self.Ts
                self.ctrlSettings.append({
                    'q0':q0,
                    'q1':q1,
                    'q2':q2,
                    'kp':Kp,
                    'ki':Ki,
                    'kd':Kd
                })

            msg = "[IrrigationControlThread] " + "control settings: " + json.dumps(self.ctrlSettings)
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

            return True
        else:
            return False

    def run(self):
        msg = "[IrrigationControlThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        flag_control = 0
        configOk = self.loadControlSettings()

        debounce_counter=0
        N_DEBOUNCE_COUNTER=10


        # watering flag shows if program is active

        while True:
            try:
                time.sleep(0.1)
                if not appVariables.queue_ws_control.empty():
                    data = appVariables.queue_ws_control.get(block=False)
                    if data != False:
                        str1 = data
                        if len(str1) != 0:
                            string = str1
                            stringArray = string.split(",")

                            if len(stringArray) > 22:
                                if(int(stringArray[0]) == 211):
                                    watering_flag = int(stringArray[22])
                                    if flag_control==0:
                                        if watering_flag==1:
                                            debounce_counter+=1
                                            if debounce_counter>N_DEBOUNCE_COUNTER:
                                                debounce_counter=0
                                                flag_control=1
                                        else:
                                            debounce_counter=0
                                    elif flag_control==2:
                                        # settings updated, waiting to finish watering program
                                        if watering_flag==0:
                                            debounce_counter+=1
                                            if debounce_counter>N_DEBOUNCE_COUNTER:
                                                debounce_counter=0
                                                flag_control=0
                                        else:
                                            debounce_counter=0


                if ((flag_control == 1) or (appVariables.flag_sim['control']==True)):
                    appVariables.flag_sim['control']=False
                    flag_control = 2 # wait until program finishes

                    msg = "[IrrigationControlThread] " + "start watering"
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                    configOk = self.loadControlSettings()
                    if configOk:
                        date1 = datetime.datetime.now()
                        timestamp = datetime.datetime.now()
                        startdate = date1 - datetime.timedelta(hours=24)
                        enddate = date1.replace(microsecond=0)
                        startdate = startdate.replace(microsecond=0)
                        print [startdate, enddate]

                        for i in range(len(self.params)):
                            js = self.params[i]
                            sid = js['sensorId']
                            msg = "[IrrigationControlThread] " + "sid: " + str(sid)
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)

                            pipeline = [{"$match": {"s_id": sid, "s_chan": 1,
                                                    "ts": {"$gt": str(startdate), "$lt": str(enddate)}}},
                                        {"$group": {"_id": "$s_id", "avg_hum": {"$avg": "$value"}}}
                                        ]
                            data = appVariables.mongomanager.aggregate_pipeline("mydb", "sensor_data", pipeline)

                            msg = "[IrrigationControlThread] " + " sensor data " + str(sid) + ": " + json.dumps(data,default=json_util.default)
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)

                            if len(data)==0:
                                continue

                            data = data[0]
                            avg_hum = data['avg_hum']
                            avg_hum = int(avg_hum)

                            msg = "[IrrigationControlThread] " + "output (average humidity): " + str(avg_hum)
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)


                            query = {"s_id": sid}
                            data = appVariables.mongomanager.find_last_records("mydb", "control_data", query,1)
                            # result = appVariables.mongomanager.find("mydb", "control_data", query)


                            newdata = {
                                "s_id": sid,
                                "ts": str(timestamp),
                                "uk1": 0,
                                "rk": js['humRef'],
                                "aux": {
                                    "uk": 0,
                                    "ek1": 0,
                                    "ek2": 0,
                                    "integral":0
                                },
                                "yk": 0
                            }
                            appVariables.mongomanager.insert("mydb", "control_data", newdata)

                            if len(data)==0:
                                data=newdata
                            else:
                                data=data[0]

                            uk1=data['aux']['uk']
                            ek1=data['aux']['ek1']
                            ek2=data['aux']['ek2']

                            if 'integral' in data['aux']:
                                integral = data['aux']['integral']
                            else:
                                integral = 0

                            msg = "[IrrigationControlThread] last control_data: " + json.dumps(data, default=json_util.default)
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)

                            if js['enabled']:
                                if js['type'] == 'pid':
                                    ek = js['humRef'] - avg_hum

                                    umin = js['umin']
                                    umax = js['umax']

                                    # ek1 is ek of previous control step
                                    # ek2 is ek1 of previous control step
                                    # ek is current error (ref - avg_hum of last period)

                                    q0 = self.ctrlSettings[i]['q0']
                                    q1 = self.ctrlSettings[i]['q0']
                                    q2 = self.ctrlSettings[i]['q0']

                                    Kp = self.ctrlSettings[i]['kp']
                                    Ki = self.ctrlSettings[i]['ki']
                                    Kd = self.ctrlSettings[i]['kd']
                                    # uk = uk1 + q0 * ek + q1 * ek1 + q2 * ek2
                                    if Ki!=0:
                                        integral = integral + ek * self.Ts

                                    derivative = (ek - ek1) / self.Ts
                                    uk = Kp * ek + Ki * integral + Kd * derivative

                                    if(uk < umin):
                                        uk = umin
                                    if(uk > umax):
                                        uk = umax

                                    uk = int(uk)

                                    # update values for pid controller
                                    # ek2 = ek1
                                    # ek1 = ek
                                    query={
                                        "s_id":sid,
                                        "ts":str(timestamp)
                                    }
                                    newdata = {
                                        "$set":{
                                            "uk1": uk1,
                                            "rk": js['humRef'],
                                            "aux": {
                                                "uk": uk,
                                                "ek1": ek,
                                                "ek2": ek1,
                                                "integral": integral
                                            },
                                            "yk": avg_hum
                                        }
                                    }
                                    appVariables.mongomanager.update("mydb", "control_data", query, newdata, ups=True)


                                msg = "[IrrigationControlThread] " + 'watering time (uk): ' + str(uk) + ' prev watering time (uk1): ' + str(uk1)
                                if not appVariables.qDebug1.full():
                                    appVariables.qDebug1.put(msg)


                                cmd = appVariables.systemSettings['codeTable']['CMD_SET_PLANT_WTIME']
                                cmdcode = cmd['cmd']
                                csv = str(cmdcode)+',' +str(js['potId']) + ',' + str(uk)

                                msg = "[IrrigationControlThread] " + csv
                                if not appVariables.qDebug1.full():
                                    appVariables.qDebug1.put(msg)

                                cmd_string = csv
                                if not appVariables.wsOutQueue.full():
                                    appVariables.wsOutQueue.put(cmd_string)

            except:
                appVariables.print_exception("[IrrigationControlThread]")

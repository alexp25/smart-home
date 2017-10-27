import time
import appVariables
import threading
from threading import Thread
from Modules.serverStat import serverStat

class ServerStatusThread(Thread):
    def run(self):
        ss={'temp':0,'cpu':0,'n_threads':0}
        serverstat = serverStat()
        msg = "[ServerStatusThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        while True:
            time.sleep(1)
            appVariables.flags["new_server_data"] = True
            ss["n_threads"] = threading.activeCount()
            if appVariables.appConfig['rpi'] == True:
                ss['temp'] = serverstat.getCPUTemperature()
                ss['cpu'] = serverstat.getCPUUsage()
            if appVariables.queueServerStat.full()==False:
                appVariables.queueServerStat.put(ss)
import time
import appVariables
import threading
from threading import Thread
from Modules.serverCmd import serverCmd
class ServerManagerThread(Thread):
    def run(self):
        server_cmd = serverCmd()
        msg = "[ServerManagerThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        db_started = False
        while True:
            if appVariables.appConfig["mongo"]:
                while not db_started:
                    msg = "[ServerManagerThread] " + "try connecting to mongodb server"
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                    if appVariables.mongomanager.connect():
                        appVariables.appConfig["mongo"] = True
                        db_started = True
                        msg = "[ServerManagerThread] " + "connected to mongodb server"
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)
                    else:
                        msg = "[ServerManagerThread] " + "error connecting to mongodb server"
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)
                        # sudo mongod --dbpath "/media/pi/RPI_DATA/database" --journal
                        # appVariables.appConfig["storage"] + "/database"
                        appVariables.appConfig["mongo"] = False
                        server_cmd.startMongoDB(appVariables.appConfig["storage"] + "/database")
                        time.sleep(30)
            time.sleep(0.5)
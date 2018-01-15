
import os
import subprocess
import sys

class serverCmd(object):
    def __init__(self):
        self.cpuTemp = 0
    def restart(self):
        command = "/usr/bin/sudo /sbin/shutdown -r now"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print output

    def startMongoDB(self, dbpath):
        # sudo mongod --dbpath "/media/pi/RPI_DATA/database" --journal
        # subprocess.call(['sudo', 'apach2ctl', 'restart'])
        FNULL = open(os.devnull, 'w')
        command = "/usr/bin/sudo mongod --dbpath " + dbpath + " --journal"
        process = subprocess.Popen(command.split(), stdout=FNULL)





import os
import subprocess
import sys

class serverCmd(object):
    def __init__(self):
        self.cpuTemp = 0
    def restart(self):
        command = "/usr/bin/sudo /sbin/shutdown -r now"
        import subprocess
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print output


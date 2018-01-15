
import os
import subprocess
import sys

class serverStat(object):
    def __init__(self):
        self.cpuTemp = 0
    def getCPUTemperature(self):
        self.cpuTemp = os.popen('vcgencmd measure_temp').readline()
        return(self.cpuTemp.replace("temp=","").replace("'C\n",""))
    def getCPUUsage(self):
        p = subprocess.Popen("vmstat 1 2|tail -1|awk '{print $15}'",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        cpu=0
        try:
            cpu = int(''.join(c for c in out if c.isdigit()))
            cpu=100-cpu
            cpu=str(cpu)
        except:
            pass

        return cpu

    def getSerialPorts(self,name):
        ##                result = subprocess.check_output(["ls","dev/tty/*"],shell=True)
        p = subprocess.Popen("ls /dev/"+name+"*",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out
    def getBluetoothDevices(self):
        p = subprocess.Popen("hcitool scan",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out
       
    

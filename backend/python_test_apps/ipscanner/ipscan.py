##import sh
##
##print "Scanning..."
### ping range 8.8.8.7 - 8.8.8.9
##for num in range(7,10):
##    # declare ip address
##    address = "192.168.1." + str(num)
##
##    # check if host is alive using PING
##    try:
##        # bash equivalent: ping -c 1 > /dev/null
##        sh.ping(address, "-c 1", _out="/dev/null")
##        print "ping to", address, "OK"
##    except sh.ErrorReturnCode_1:
##        print "no response from", address


import os
import subprocess
from socket import *

##def ping(host):
##    """
##    Returns True if host responds to a ping request
##    """
##    import os, platform
##
##    # Ping parameters as function of OS
##    if  platform.system().lower()=="windows":
##        ping_str = "-n 1"
##    else:
##        ping_str = "-c 1"
##        
##    # Ping
##    return os.system("ping " + ping_str + " " + host)

def ping(host):
    ping_response = subprocess.Popen(["ping", hostname, "-n", '1', "-w" , '200'], stdout=subprocess.PIPE).stdout.read()
    if ('unreachable' in ping_response or 'timed out' in ping_response):
        return False
    else:
        return True

nodeList = [];

for num in range (1,10):
    hostname = "192.168.1."+str(num)
    isAlive = ping(hostname)
    print hostname + ': ' + str(isAlive)
    if(isAlive):
##        print getfqdn(hostname)
        try:
            print gethostbyaddr(hostname)
        except:
            print 'cannot resolve host'
        nodeList.append(hostname);

print nodeList        


##print ping(hostname)
##response = os.system("ping -c 1 " + hostname)
##
###and then check the response...
##if response == 0:
##  print hostname, 'is up!'
##else:
##  print hostname, 'is down!'



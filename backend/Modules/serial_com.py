import threading
import time
import serial
import traceback

import datetime

import Queue
queue_write = Queue.Queue(maxsize=10)
queue_read = Queue.Queue(maxsize=10)

serial_com_port = None
serial_com_port_status = True
serial_com_port_name = None
serial_com_port_baud_rate = None


class serialReadThread (threading.Thread):
        def __init__(self,threadID,name):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self._stop = threading.Event()
                self._req = threading.Event()
                self.time1 = time.time()
                self.data = 0
                self.data_received = 0
                self.receivedFlag = False


        def stop(self):
                self._stop.set()
                print("thread "+self.name+" stop event registered\n")

        def stopped(self):
                return self._stop.isSet()

        def run(self):
                global queue_read
                global serial_com_port
                global serial_com_port_status
                global serial_com_port_name, serial_com_port_baud_rate

                print("starting " + self.name + " thread\n")
                line=''
                while True:
                    try:
                        # if serial_com_port.isOpen() == True:

                        c = serial_com_port.read()
                        line += c
                        if c=='\n':
                            if queue_read.full() == False:
                                queue_read.put(line)
                            line = ''

                        # serial_com_port_status = True
                    except:
                        print "serial read thread exception"
                        serial_com_port_status = False
                        # traceback.print_exc()
                        time.sleep(10)
                        # try to open the com port again
                        print "opening serial port..."
                        try:
                            if serial_com_port.isOpen() == True:
                                serial_com_port.close()
                            serial_com_port = serial.Serial(serial_com_port_name, serial_com_port_baud_rate, timeout=3)
                            print "serial port open"
                        except:
                            print "could not open serial port"

                    if self.stopped():
                        print("thread " + self.name + " stop event detected\n")
                        break

                if serial_com_port.isOpen() == True:
                    serial_com_port.close()
                print("exiting " + self.name +" thread")


class serialWriteThread (threading.Thread):
        def __init__(self,threadID,name):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self._stop = threading.Event()
                self._req = threading.Event()

        def stop(self):
                self._stop.set()
                print("thread "+self.name+" stop event registered\n")
        def stopped(self):
                return self._stop.isSet()

        def run(self):
                global queue_write
                global serial_com_port
                global serial_com_port_status

                print("starting " + self.name + " thread\n")
                while True:
                    if self.stopped():
                        print("thread " + self.name + " stop event detected\n")
                        break

                    try:
                        if serial_com_port.isOpen() == True:
                            if queue_write.empty() == False:
                                result = queue_write.get(block=False)
                                # print 'write ' + result
                                serial_com_port.write(result)
                                # print 'write ok'
                    except:
                            print "serial write thread exception"
                            # traceback.print_exc()
                            time.sleep(3)

                print("exiting " + self.name +" thread")

class serialCom(object):
    def __init__(self,portName,baudRate):
        self.threads = []
        self.start_time = 0
        self.elapsed_time = 0
        self.portName = portName
        self.baudRate = baudRate
        self.start_sending_data = False

    def config(self,portName,baudRate):
        self.portName = portName
        self.baudRate = baudRate

    def start(self):
        global serial_com_port
        global serial_com_port_name, serial_com_port_baud_rate
        serial_com_port_name = self.portName
        serial_com_port_baud_rate = self.baudRate

        if not (self.threads):
                try:
                        serial_com_port = serial.Serial(self.portName, self.baudRate, timeout=3)

                        print("starting thread")
                        thread1 = serialReadThread(1, "serialReadThread")
                        print("t1 create")
                        thread2 = serialWriteThread(2, "serialWriteThread")
                        print("t2 create")
                        thread1.start()
                        print("t1 start")
                        thread2.start()
                        print("t2 start")
                        self.threads.append(thread1)
                        self.threads.append(thread2)
                except:
                        message = 'serial exception: ' + traceback.format_exc()
                        print message


    def stop(self):
        print 'serialCom stop'
        if self.threads:
            for i in range(len(self.threads)):
                self.threads[i].stop()
                self.threads[i].join()
            self.threads = []

    def send(self,msg):
        global queue_write
        # print 'send: ' + msg
        queue_write.put(msg)
        return True

    def get_received_data(self):
        global queue_read
        result = None
        if self.threads:
            if queue_read.empty() == False:
                result = queue_read.get(block=False)
        return result


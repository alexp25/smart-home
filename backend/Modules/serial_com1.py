import threading
import time
import serial
import traceback

from Queue import Queue

code = 211
requestBody = ''
requestBodyEn = False

q1 = Queue(maxsize=1)
q2 = Queue(maxsize=1)


class myThread (threading.Thread):
        def __init__(self,threadID,name,ser):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self._stop = threading.Event()
                self._req = threading.Event()
                self.time1 = time.time()
                self.ser = ser
                
        def stop(self):
                self._stop.set()
                print("thread "+self.name+" stop event registered\n")
                       
        def stopped(self):
                return self._stop.isSet()

        def serial_data(self):
            while True:
                yield self.ser.readline()
    
        def run(self):
                global q1
                print("starting " + self.name + " thread\n")

                for line in self.serial_data():
                        if not q1.full():
                                q1.put(line)
                        if self.stopped():
                                print("thread "+self.name+" stop event detected\n")
                                break
                                        
                if self.ser.isOpen() == True:                       
                        self.ser.close()               
                print("exiting " + self.name +" thread")


class myThread2 (threading.Thread):
        def __init__(self,threadID,name,ser,interval):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self._stop = threading.Event()
                self._req = threading.Event()
                self.ser = ser
                self.interval = interval
    
                
        def stop(self):
                self._stop.set()
                print("thread "+self.name+" stop event registered\n")
        def stopped(self):
                return self._stop.isSet()
        
        def run(self):
                global q2                
                print("starting " + self.name + " thread\n")   
                while True:
                        time.sleep(self.interval)
                        try:                                
                                if not q2.empty():
                                        obj = q2.get()

                                        with q2.mutex:
                                                q2.queue.clear()
                                                
                                        dig = list(int(d) for d in str(obj['code']))
                                        
                                        if self.ser.isOpen() == True:   
                                                for i in range(len(dig)):
                                                        self.ser.write(chr(dig[i]))
                                                        
                                                if (obj['hasbody']==True):
                                                        self.ser.write(obj['body'])
                                                        self.ser.write("\n")
                                        else:
                                                self.ser.close()
                                                self.ser.open()
                                                traceback.print_exc()
                                                time.sleep(5)
                                                
                                if self.ser.isOpen() == True:   
                                        dig = list(int(d) for d in str(211))
                                        for i in range(len(dig)):
                                                self.ser.write(chr(dig[i]))
                                else:
                                        self.ser.close()
                                        self.ser.open()
                                        traceback.print_exc()
                                        time.sleep(5)
                                        
                        except:
                                print("bluetooth write exception thread 2")
                                self.ser.close()
                                self.ser.open() 
##                                traceback.print_exc()
                                time.sleep(5)

                if self.ser.isOpen() == True:                       
                        self.ser.close()  
                print("exiting " + self.name +" thread")


##threadLock = threading.Lock()


class serialArduino(object):
	def __init__(self,portName,interval):
		self.threads = []
		self.start_time = 0
		self.elapsed_time = 0
		self.portName = portName
		self.interval = interval
		self.start_sending_data = False
		
		self.start()                
        
	def start(self):
                try:
                        if not(self.threads):
                                self.ser = serial.Serial(self.portName,38400,timeout=3)
                                print("starting thread")
                                thread1 = myThread(1, "bluetooth serial",self.ser)
                                print("t1 create");
                                thread2 = myThread2(2, "bluetooth serial ask",self.ser,self.interval)
                                print("t2 create");
                                thread1.start()
                                print("t1 start");
                                thread2.start()
                                print("t2 start");
                                self.threads.append(thread1)
                                self.threads.append(thread2)
                        else:
                                self.stop()
                                self.ser = serial.Serial(self.portName,38400,timeout=3)
                                print("starting thread")
                                thread1 = myThread(1, "bluetooth serial",self.ser)
                                print("t1 create");
                                thread2 = myThread2(2, "bluetooth serial ask",self.ser,self.interval)
                                print("t2 create");
                                thread1.start()
                                print("t1 start");
                                thread2.start()
                                print("t2 start");
                                self.threads.append(thread1)
                                self.threads.append(thread2)
                                
                except:
                        print ("could not open serial port")
                        self.stop()
			
	def stop(self):
		if self.threads:
			for i in range(1):
				self.threads[i].stop()
				self.threads[i].join()
			self.threads = []
			
	def send(self,dig,bodyEn,body):
                global q2

                obj = {'code':dig,'hasbody':bodyEn,'body':body}
                q2.put(obj)
                
                print obj
                return True
 
	def get_received_data(self):
                global q1
                if self.threads:
                        data = False
                        try:
                                data = q1.get(block=True,timeout=1)
                        except:
                                print 'get data timeout'
                                pass
                        finally:
                                return data
                else:
                        return False


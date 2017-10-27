import io
import time
import threading
import time
w=320
h=240
class myThread (threading.Thread):
	def __init__(self,threadID,name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self._stop = threading.Event()
		self._req = threading.Event()

		self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
	def stop(self):
		self._stop.set()
		print("stop self")
	def stopped(self):
		return self._stop.isSet()
	def req(self):        
		self._req.set()
	def requested(self):
		return self._req.isSet()
	
	def run(self):
		global image 
		count = 0
		start_time = time.time()
		while True:
			if self.stopped():
				break
				
			time.sleep(0.1)
			if self.requested():
				self._req.clear()
				start_time = time.time()
			elapsed_time = time.time() - start_time
##			print elapsed_time
			if elapsed_time > 5:
				time.sleep(0.9)
				continue   
			image = self.frames[count]
			count = count + 1
			if count > 2:
			   count = 0

				
			
threadLock = threading.Lock()

class Camera1(object):
	def __init__(self):
		self.threads = []
		self.start_time = time.time()
		self.elapsed_time = 0
		if not(self.threads):
			print("starting thread")
                        thread1 = myThread(1, "thread1")
			thread1.start()
			self.threads.append(thread1)
			
	def start(self):
		if not(self.threads):
			print("starting thread")
			thread1 = myThread(1, "thread1")
			thread1.start()
			self.threads.append(thread1)
			
	def stop(self):
		if self.threads:
			print("stopping thread")
			for i in range(1):
				self.threads[i].stop()
				self.threads[i].join()
			self.threads = []
			
	def get_frame(self):
		if self.threads:
			for i in range(1):
				self.threads[i].req()
		else:
			self.start()
			for i in range(1):
				self.threads[i].req()

		self.start_time = time.time()
		
		return image


import io
import time
import picamera
##import cv2
import numpy as np
from picamera.array import PiRGBArray
import threading
import time

class myThread (threading.Thread):
	def __init__(self,threadID,name,w,h):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self._stop = threading.Event()
		self._req = threading.Event()
		self.start_time = time.time()
		self.elapsed_time = 0
		self.w = w
		self.h = h
	def stop(self):
		self._stop.set()
		print("thread "+self.name+" stop event registered\n")
	def stopped(self):
		return self._stop.isSet()
	def req(self):
		self._req.set()
	def requested(self):
		return self._req.isSet()
	
	def run(self):
		global image
		print("starting " + self.name + " thread\n")
		with picamera.PiCamera() as camera:
			camera.resolution = (self.w, self.h)
			camera.framerate = 24
			stream = io.BytesIO()
			start_time = time.time()
			#For the mjpeg format, use JPEG quality values between 1 and 100 (where higher values are higher quality). 
			for foo in camera.capture_continuous(stream, format='jpeg',use_video_port=True,quality=40):
				# Truncate the stream to the current position (in case
				# prior iterations output a longer image)
				stream.seek(0)
				image = stream.read()
				stream.seek(0)
				stream.truncate()

				self.elapsed_time = time.time() - self.start_time

				if self.requested():
                                    self._req.clear()
                                    self.start_time = time.time()
                                    self.elapsed_time = 0
                                
                                if self.elapsed_time > 5:
                                    time.sleep(1)
##                                    print self.elapsed_time
                                    
				if self.stopped():
					break
		print("exiting " + self.name + " thread\n")
				  
threadLock = threading.Lock()


class Camera1(object):
	def __init__(self, w, h):
		self.threads = []
		self.start_time = time.time()
		self.elapsed_time = 0
		if not(self.threads):
			thread1 = myThread(1, "picamera", w, h)
			thread1.start()
			self.threads.append(thread1)
			
	def start(self):
		if not(self.threads):
			thread1 = myThread(1, "picamera")
			thread1.start()
			self.threads.append(thread1)
			
	def stop(self):
		if self.threads:
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




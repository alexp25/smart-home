import io
import time
import picamera

from picamera.array import PiRGBArray
import threading
import time

import numpy as np

import datetime
from multiprocessing import Process, Queue

import sys

import appVariables


image = False
snapshot = False
processed_flag = False
retval = None
image_processed_encoded = None

video_writer=None



class RecordingThread(threading.Thread):
    def __init__(self, threadID, name, q_rec, q_dbg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q_rec = q_rec

        self.qDebug1 = q_dbg
    def run(self):
        global video_writer

        msg = "starting " + self.name + " thread"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)

        while True:
            time.sleep(0.01)
            try:
                while self.q_rec.empty()==False:
                    frame = self.q_rec.get(block=False)
                    if video_writer is not None:
                        video_writer.write(frame)
                    else:
                        msg = "video writer not initialized"
                        if self.qDebug1.full() == False:
                            self.qDebug1.put(msg)
            except:
                exc_type, exc_value = sys.exc_info()[:2]
                exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
                msg = self.name + ' thread error: ' + exceptionMessage
                if self.qDebug1.full() == False:
                    self.qDebug1.put(msg)

class ProcessingThread(threading.Thread):
    def __init__(self, threadID, name, q_image_in, q_image_out, q_res, q_dbg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q_image_in = q_image_in
        self.q_image_out = q_image_out

        self.qDebug1 = q_dbg
        self.q_result = q_res

    def run(self):
        global image_processed_encoded
        imagecv_processed = None
        avg = None
        msg = "starting " + self.name + " thread"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)
        while True:
            time.sleep(0.01)
            try:
                if self.q_image_in.empty()==False:
                    imagecv = self.q_image_in.get(block=False)

                    if self.q_image_out.full() == False:
                        self.q_image_out.put(imagecv)

            except:
                exc_type, exc_value = sys.exc_info()[:2]
                exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
                msg = self.name + ' thread error: '+exceptionMessage
                if self.qDebug1.full() == False:
                    self.qDebug1.put(msg)


class CameraThread(threading.Thread):
    def __init__(self, threadID, name, w, h, q_image, q_image2, q_rec, q_dbg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stop = threading.Event()
        self._req = threading.Event()
        self._snap = threading.Event()
        self._process = threading.Event()
        self._rec = threading.Event()
        self._norec = threading.Event()
        self.w = w
        self.h = h
        self.flag_recording=False

        self.q_image = q_image
        self.q_rec = q_rec
        self.q_image2 = q_image2

        self.qDebug1 = q_dbg

    def stop(self):
        self._stop.set()
        msg = "thread " + self.name + " stop event registered"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)

    def stopped(self):
        return self._stop.isSet()

    def req(self):
        self._req.set()

    def requested(self):
        return self._req.isSet()

    def take_snapshot(self):
        self._snap.set()

    def requested_snapshot(self):
        return self._snap.isSet()

    def requested_start_recording(self):
        return self._rec.isSet()

    def start_recording(self):
        self._rec.set()

    def requested_stop_recording(self):
        return self._norec.isSet()

    def stop_recording(self):
        self._norec.set()

    def isRecording(self):
        return self.flag_recording


    def run(self):
        global image
        global snapshot
        global processed_flag
        global retval
        global video_writer
        first_snapshots = 5
        msg = "starting " + self.name + " thread"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)


        fps = 24

        elapsed_time_request=0
        start_time_request = time.time()

        elapsed_time_processed_video = 0
        start_time_processed_video = time.time()
        fps_processed_min=1
        fps_processed_max=5
        fps_processed=2

        self.flag_recording=False
        start_time_record = time.time()
        max_time_record = 60*30

        with picamera.PiCamera() as camera:
            camera.resolution = (self.w, self.h)

            # imgbuf = np.zeros((self.w, self.h), dtype=np.uint8)

            camera.framerate = fps
            stream = io.BytesIO()
            start_time = time.time()
            # For the mjpeg format, use JPEG quality values between 1 and 100 (where higher values are higher quality).
            for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True, quality=50):
                # Truncate the stream to the current position (in case
                # prior iterations output a longer image)
                stream.seek(0)
                image = stream.read()

                imagecv = np.fromstring(image, dtype=np.uint8)

                time_crt = time.time()
                if time_crt - start_time_processed_video >= fps_processed:
                    start_time_processed_video = time_crt
                    ## process image
                    if self.q_image2.full()==False:
                        self.q_image2.put(image)

                if self.q_image.full() == False:
                    self.q_image.put(image)

                stream.seek(0)
                stream.truncate()

                elapsed_time_request = time_crt - start_time_request
                if self.requested():
                    self._req.clear()
                    start_time_request = time_crt
                    elapsed_time_request = 0
                    fps_processed = fps_processed_min

                if elapsed_time_request > 5:
                    fps_processed = fps_processed_max
                    # time.sleep(0.5)

                if time_crt - start_time_record > max_time_record:
                    video_writer = None
                    self.flag_recording = False

                if self.stopped():
                    break

        msg = "exiting " + self.name + " thread"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)


class Camera1(object):
    def __init__(self, w, h, qDebug1):
        self.cameraThread=None
        self.start_time = time.time()
        self.elapsed_time = 0

        self.q_image = Queue(maxsize=1)
        self.q_image_proc = Queue(maxsize=1)
        self.q_image2 = Queue(maxsize=1)
        self.q_rec = Queue(maxsize=5)
        self.q_result = Queue(maxsize=1)

        self.w=w
        self.h=h

        self.qDebug1 = qDebug1

        self.cameraThread=None
        self.processingThread=None
        self.recordingThread=None

        msg = "starting camera threads"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)

        self.start()

    def start(self):
        if self.cameraThread is None:
            self.cameraThread = CameraThread(1, "picamera", self.w, self.h, q_image=self.q_image, q_image2=self.q_image2,
                                         q_rec=self.q_rec, q_dbg=self.qDebug1)
            self.cameraThread.start()
        if self.processingThread is None:
            self.processingThread = ProcessingThread(2, "videoproc", q_image_in=self.q_image2,
                                                     q_image_out=self.q_image_proc, q_res=self.q_result, q_dbg=self.qDebug1)
            self.processingThread.start()
        if self.recordingThread is None:
            self.recordingThread = RecordingThread(3, "videorec", q_rec=self.q_rec, q_dbg=self.qDebug1)
            self.recordingThread.start()

    def stop(self):
        if self.cameraThread is not None:
            self.cameraThread.stop()
            self.cameraThread.join()
            self.cameraThread = None
        if self.processingThread is not None:
            self.processingThread.stop()
            self.processingThread.join()
            self.processingThread = None
        if self.recordingThread is not None:
            self.recordingThread.stop()
            self.recordingThread.join()
            self.recordingThread = None

    def get_frame(self):
        global image
        if self.cameraThread is not None:
            self.cameraThread.req()
        else:
            self.start()
            self.cameraThread.req()
        self.start_time = time.time()
        while self.q_image.empty():
            time.sleep(0.05)
        return self.q_image.get(block=False)

    def has_frame(self):
        return not self.q_image.empty()

    def has_processed_frame(self):
        return not self.q_image_proc.empty()

    def get_processed_frame(self):
        if self.cameraThread is not None:
            self.cameraThread.req()
        else:
            self.start()
            self.cameraThread.req()
        self.start_time = time.time()
        while self.q_image_proc.empty():
            time.sleep(0.05)
        return self.q_image_proc.get(block=False)

    def get_processing_result(self):
        result = None
        if not self.q_result.empty():
            result = self.q_result.get(block=False)
        return result

    def take_snapshot(self):
        if self.cameraThread is not None:
            self.cameraThread.req()
            self.cameraThread.take_snapshot()
        return

    def start_recording(self):
        if self.cameraThread is not None:
            self.cameraThread.start_recording()
        return

    def stop_recording(self):
        if self.cameraThread is not None:
            self.cameraThread.stop_recording()
        return

    def isRecording(self):
        if self.cameraThread is not None:
            return self.cameraThread.isRecording()
        else:
            return False


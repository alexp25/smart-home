import threading
import time

import cv2
import numpy as np
import urllib

from multiprocessing import Queue
import appVariables
import datetime

image = False
snapshot = False
processed_flag = False
retval = None
image_processed_encoded = None
video_writer=None

class CameraThreadRemote(threading.Thread):
    def __init__(self, threadID, name, url, q_image):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stop = threading.Event()
        self._req = threading.Event()
        self._running = threading.Event()
        self.q_image = q_image

        self.url = url

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def is_running(self):
        self._running.isSet()

    def requested(self):
        return self._req.isSet()

    def isRecording(self):
        return self.flag_recording


    def run(self):
        global image
        global snapshot
        global processed_flag
        global retval
        global video_writer
        msg = "starting " + self.name + " thread, url: "+str(self.url)
        if appVariables.qDebug1.full() == False:
            appVariables.qDebug1.put(msg)

        if self.url is None:
            pass
        else:
            try:
                stream = urllib.urlopen(self.url)
                print(stream)
                bytes = ''

                self._running.set()

                while True:
                    bytes += stream.read(1024)
                    a = bytes.find('\xff\xd8')
                    b = bytes.find('\xff\xd9')
                    if a != -1 and b != -1:
                        # print('stream')
                        image = bytes[a:b + 2]
                        bytes = bytes[b + 2:]

                        imagecv = np.fromstring(image, dtype=np.uint8)
                        imagecv = cv2.imdecode(imagecv, 1)

                        cv2.putText(imagecv, datetime.datetime.now().strftime("%I:%M:%S.%f"),
                                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                        (retval, image_processed_encoded) = cv2.imencode('.jpg', imagecv)
                        image_processed_encoded = bytearray(image_processed_encoded)

                        # imagecv = bytearray(jpg)
                        if self.q_image.full() == False:
                            self.q_image.put(image_processed_encoded)

                        if self.stopped():
                            break
            except:
                appVariables.print_exception("[camera_remote] ")

        msg = "exiting " + self.name + " thread"
        if appVariables.qDebug1.full() == False:
            appVariables.qDebug1.put(msg)

        self._running.clear()


class Camera2(object):
    def __init__(self, url, qDebug1):
        self.cameraThread=None
        self.start_time = time.time()
        self.elapsed_time = 0

        self.q_image = Queue(maxsize=1)

        self.url=url
        self.qDebug1 = qDebug1
        self.cameraThread=None


        msg = "starting camera remote threads"
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)
        self.start()

    def set_url(self,url):
        msg = "set url: " + url
        if self.qDebug1.full() == False:
            self.qDebug1.put(msg)
        self.url = url

    def start(self):

        if self.cameraThread is None:
            self.cameraThread = CameraThreadRemote(1, "camera_remote", url=self.url, q_image=self.q_image)
            self.cameraThread.start()
        else:
            if not self.cameraThread.is_running():
                self.stop()
                self.start()

    def stop(self):
        if self.cameraThread is not None:
            self.cameraThread.stop()
            self.cameraThread.join()
            self.cameraThread = None

    def get_frame(self):
        global image
        if self.cameraThread is not None:
            pass
        else:
            self.start()
        if not self.q_image.empty():
            return self.q_image.get(block=False)
        else:
            return None

    def has_frame(self):
        return not self.q_image.empty()



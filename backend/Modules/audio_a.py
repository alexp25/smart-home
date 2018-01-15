from sys import byteorder
from array import array
from struct import pack

import pyaudio
import numpy as np

import threading
import time
import sys


from multiprocessing import Process, Queue

fftString=''
stringReady = False


def filter_lpf(data,new_data,alpha):
    dataf = data*alpha + new_data*(1-alpha)
    return dataf

def audioProcess(q,qCmd,qInfo):
    stop_flag=0
    sampFreq = 44100
    CHUNK_SIZE = 256

    n_levels = 11
    fftData2 = np.empty(n_levels)

    params = {
        "flag_filter_audio": True,
        "flag_filter_fft": False,
        "audio_low_pass_fc": 50,
        "audio_high_pass_fc": 10000,
        "fft_low_pass_fc": 50,
        "fft_sampling_rate": 178,
        "min_fft_val":20
    }

    params2 = {
        "alpha_sound_high_pass":0,
        "alpha_sound_low_pass":0,
        "alpha_fft_low_pass":0
    }

    def calculate_params(params):
        fc = params["audio_low_pass_fc"]
        RC = 1.0 / fc / 6.28
        Ts = 1.0 / sampFreq
        params2["alpha_sound_high_pass"] = RC / (RC + Ts)

        fc = 10000
        RC = 1.0 / fc / 6.28
        params2["alpha_sound_low_pass"] = RC / (RC + Ts)

        fs_fft = params["fft_sampling_rate"]
        Ts = 1.0 / fs_fft
        fc_fft = params["fft_low_pass_fc"]
        RC = 1.0 / fc_fft / 6.28
        params2["alpha_fft_low_pass"] = RC / (RC + Ts)

        return params2

    params2=calculate_params(params)

    running = False

    p = pyaudio.PyAudio()
    ndevice = p.get_device_count()
    devname='C-Media USB Headphone Set'
    # devname='Microphone (SB X-Fi Xtreme Audi'
    devindex=0


    for i in range(ndevice):
        try:
            devinfo=p.get_device_info_by_index(i)
            devname_crt=devinfo['name']
            # print(str(i)+'.'+devname_crt+', input channels: '+str(devinfo['maxInputChannels']))
            if devname in devname_crt:
                # print 'selected'
                devindex=i
        except:
            print 'no audio device'

    try:
        # test (pc): input_device_index=3
        # rpi: input_device_index=5
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sampFreq,
            input_device_index=devindex,
            input=True,
            frames_per_buffer=CHUNK_SIZE)
        sound_ok = True
        print('sound ok')
    except:
        sound_ok = False
        print('sound error')


    if sound_ok:
        while True:
            # little endian, signed short
            if not qCmd.empty():
                cmd = qCmd.get(block=False)
                if cmd[0] == 'stop':
                    running = False
                if cmd[0] == 'start':
                    running = True
                if cmd[0] == 'params':
                    params = cmd[1]
                    params2 = calculate_params(params)
                if cmd[0] == 'get-params':
                    if qInfo.full() == False:
                        qInfo.put(params)

            if running and sound_ok:
                # do this as long as you want fresh samples
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                indata = np.fromstring(data, dtype=np.int16)

                # scale to 0..100
                LIMIT_SUP = 16384
                indata[0] = indata[0] * 100 / LIMIT_SUP

                for i in range(1,len(indata)):
                    if params["flag_filter_audio"]:
                        # low pass
                        indata[i] = indata[i-1] * params2["alpha_sound_low_pass"] + indata[i] * (1-params2["alpha_sound_low_pass"])
                        # high pass 50 hz
                        # indata[i] = indata[i - 1] * params2["alpha_sound_high_pass"] + (indata[i] - indata[i-1]) * params2["alpha_sound_high_pass"]
                    # limit
                    indata[i] = indata[i] * 100 / LIMIT_SUP

                # Take the fft and square each value
                fftData = abs(np.fft.rfft(indata)) ** 2
                fftData = np.sqrt(fftData)

                # fftData = fftData[2:len(fftData)]

                # resample to 10 frequency bands
                m = len(fftData)
                fftData1 = np.interp(np.linspace(0, m - 1, n_levels), np.arange(m), fftData)

                if not params["flag_filter_fft"]:
                    fftData2 = fftData1

                for ifft in range(n_levels):
                    # print fftData1List[0]
                    # print fftData1List[ifft]
                    # filter fft data (power spectrum) to keep beats longer
                    if params["flag_filter_fft"]:
                        fftData2[ifft] = fftData2[ifft]*params2["alpha_fft_low_pass"]+(fftData1[ifft])*(1-params2["alpha_fft_low_pass"])

                    if fftData2[ifft]>100:
                        fftData2[ifft]=100
                    if fftData2[ifft]<params["min_fft_val"]:
                        fftData2[ifft]=params["min_fft_val"]

                # print len(fftData2)
                # print fftData2

                # resample data to fit n elements, for display in app
                n = 100
                m = len(indata)
                indata1 = np.interp(np.linspace(0, m - 1, n), np.arange(m), indata)

                # print fftData2
                fftData3=fftData2[1:n_levels]
                # print fftData2
                fftString = ''
                for ifft in range(n_levels-1):
                    # fftData[i] = fftData[i] * 100 / LIMIT_SUP
                    fftString += str(int(fftData3[ifft]))
                    if ifft < n_levels-2:
                        fftString += ','


                result = {
                    'fftString': fftString,
                    'fft': fftData3.tolist(),
                    'rawData': indata1.tolist()
                }
                if q.full()==False:
                    q.put(result)
            else:
                time.sleep(0.1)

    print("exiting audio process")

class audioAnalyzer(object):
    def __init__(self):
        self.q = Queue(maxsize=5)
        self.qCmd = Queue(maxsize=1)
        self.qInfo = Queue(maxsize=1)
        # print("starting thread")
        # self.thread1 = myThread(1, "audio thread")
        # print("t1 create");
        # self.thread1.start()
        # print("t1 start");
        self.p = None
        if self.p is None:
            self.p = Process(target=audioProcess, args=(self.q, self.qCmd, self.qInfo))
        self.p.start()

    def set_params(self,params):
        while self.qCmd.full():
            time.sleep(0.1)
        self.qCmd.put(('params',params))

    def get_params(self):
        while self.qCmd.full():
            time.sleep(0.1)
        self.qCmd.put(('get-params',None))
        while self.qInfo.empty():
            time.sleep(0.1)
        return self.qInfo.get(block=False)

    def stop(self):
        while self.qCmd.full():
            time.sleep(0.1)
        self.qCmd.put(("stop",None))
    def start(self):
        while self.qCmd.full():
            time.sleep(0.1)
        self.qCmd.put(("start",None))

    def getData(self):
        data = None
        if not self.q.empty():
            data = self.q.get(block=False)
        return data

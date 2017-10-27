import time
import appVariables
from threading import Thread

class SoundDataThread(Thread):
    def run(self):
        dt_min=0.05
        t0=time.time()
        msg = "[SoundDataThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        while True:
            time.sleep(0.01)
            audioData = appVariables.audio_a1.getData()
            # print ('soundData')
            # print(audioData)
            t1=time.time()
            if audioData is not None:
                if not (appVariables.qAudioData.full()):
                    appVariables.qAudioData.put(audioData)

                if (t1-t0)>dt_min and not (appVariables.qAudioData2.full()):
                    t0=t1
                    appVariables.qAudioData2.put(audioData)
import time
import appVariables
import datetime
from threading import Thread
import sys

class DebugPrintThread(Thread):
    def run(self):
        n_max_log=50
        dt_log=60
        t0_log=time.time()

        data_source=[
            {
                'q':appVariables.qTCPIn,
                'buf':[],
                'cnt':0,
                'first':True,
                'file':appVariables.appConfig["storage"] + "/" + appVariables.appConfig['log_file_tcp_in'],
                't1':t0_log,
                'print':False,
                'q_forward':None
            },
            {
                'q': appVariables.qTCPOut,
                'buf': [],
                'cnt': 0,
                'first': True,
                'file':appVariables.appConfig["storage"] + "/" + appVariables.appConfig['log_file_tcp_out'],
                't1':t0_log,
                'print':False,
                'q_forward':None
            },
            {
                'q': appVariables.qDebug1,
                'buf': [],
                'cnt': 0,
                'first': True,
                'file':appVariables.appConfig["storage"] + "/" + appVariables.appConfig['log_file_stdout'],
                't1':t0_log,
                'print':True,
                'q_forward':appVariables.qDebug2
            }
        ]

        msg = "[DebugPrintThread] " + "running"
        print(msg)

        while True:
            time.sleep(0.1)
            t1=time.time()
            for s in data_source:
                if not s['q'].empty():
                    dtime=datetime.datetime.now()
                    crt_time = dtime.strftime("%H:%M:%S.%f")
                    p = crt_time + ': ' + s['q'].get(block=False)

                    if s['print']:
                        print(p)
                    if s['q_forward'] is not None:
                        appVariables.flags["new_server_data"] = True
                        if not s['q_forward'].full():
                            s['q_forward'].put(p)

                    # also add date to log file
                    p = str(dtime.date()) + ' ' + p
                    s['buf'].append(p)
                    s['cnt'] += 1
                # write buffer log to file every dt (if new elements), or every n elements
                if (s['cnt'] >= n_max_log) or (((t1 - s['t1']) >= dt_log) and (s['cnt'] > 0)):
                    s['cnt'] = 0
                    if appVariables.appConfig["enable_log"]:
                        open_style = "a"
                        if s['first']:
                            open_style = "w"
                            s['first'] = False
                        try:
                            with open(s['file'], open_style) as myfile:
                                for e in s['buf']:
                                    myfile.write(e + '\r\n')
                        except:
                            print(appVariables.format_exception(""))
                    s['buf'] = []

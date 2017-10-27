
#main process sends data to child process via queue

from multiprocessing import Process, Queue
import time
import sys

def f(q,name):
    stop_flag=0
    while True:
        while not q.empty():
            try:
                data = q.get(False)

                if data[0] == -1:
                    stop_flag=1
                q.put("ok");
            except Empty:
                continue
        if (stop_flag):
            break
        time.sleep(0.1)
           
    

if __name__ == '__main__':
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()

    for i in range(5):
        q.put([i, None, 'hello'])
        time.sleep(1)
        print q.get()

    q.put([-1, None, 'stop'])
##    
    p.join()

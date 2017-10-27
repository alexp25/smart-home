import time
import appVariables
import threading
from threading import Thread
import sys
import socket
import select
import copy
from multiprocessing import Queue

TCP_IP = '0.0.0.0'
TCP_PORT = 8050
BUFFER_SIZE = 1024  # 20. Normally 1024, but we want fast response

class TCPServerThread(Thread):
    def __init__(self, q_read, q_write):
        threading.Thread.__init__(self)
        self._stopper = threading.Event()
        self.q_read = q_read
        self.q_write = q_write

    def run(self):
        global TCP_IP, TCP_PORT, BUFFER_SIZE
        time.sleep(5)
        msg = "[TCPServerThread] " + "running"
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setblocking(0)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((TCP_IP, TCP_PORT))
            server.listen(5)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)

            msg = "[TCPServerThread] exception: " + exceptionMessage
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)
            return

        # Sockets from which we expect to read
        inputs = [server]

        # Sockets to which we expect to write
        outputs = []

        # Outgoing message queues (socket:Queue)
        message_queues = {}

        appVariables.clientList = []
        appVariables.clientInfoList = []
        appVariables.clientListFcn = []
        connectionDataBuffer = {}

        t0 = time.time()

        while inputs:
            # Wait for at least one of the sockets to be ready for processing
            # print >> sys.stderr, '\nwaiting for the next event'
            # time.sleep(0.001)
            readable, writable, exceptional = select.select(inputs, outputs, inputs, 0.1)
            t1 = time.time()

            # Handle inputs
            for s in readable:
                if s is server:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()

                    msg = "[TCPServerThread] " + 'new connection ' + str(connection) + ' from ' + str(client_address)
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                    connection.setblocking(0)
                    inputs.append(connection)
                    outputs.append(connection)

                    # Give the connection a queue for data we want to send

                    connectionDataBuffer[connection] = {
                        'str': '',
                        'index': 0
                    }
                    # check if ip is already in connected client list
                    # if true then only replace properties
                    # if false then create a new object
                    clientInList = False
                    for i in range(len(appVariables.clientListFcn)):
                        if appVariables.clientList[i]['ip'] == client_address[0]:
                            clientInList = True

                            appVariables.clientList[i]['id'] = 0
                            appVariables.clientListFcn[i]['connection'] = connection
                            appVariables.clientListFcn[i]['t0'] = t1
                            appVariables.clientListFcn[i]['t0_polling'] = t1
                            appVariables.clientListFcn[i]['t0_log'] = t1
                            break

                    if not clientInList:
                        newClientFcn = copy.deepcopy(appVariables.clientModelFcn)
                        newClientFcn['connection'] = connection
                        newClientFcn['q_in'] = Queue(maxsize=10)
                        newClientFcn['q_out'] = Queue(maxsize=10)
                        newClientFcn['t0'] = t1
                        newClientFcn['t0_polling'] = t1
                        newClientFcn['t0_log'] = t1
                        appVariables.clientListFcn.append(newClientFcn)
                        newClient = copy.deepcopy(appVariables.clientModel)
                        newClient['counter_rx'] = 0
                        newClient['counter_tx'] = 0
                        appVariables.clientList.append(newClient)
                        appVariables.clientInfoList.append({'id':0,'ip':0,'type':0})
                        # print(appVariables.clientList)
                else:
                    try:
                        data = s.recv(1)
                        # print(data)
                        if data:
                            # A readable client socket has data
                            # print >> sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                            connectionDataBuffer[s]['str'] += data
                            connectionDataBuffer[s]['index'] += 1
                            if ((data == '\n') or (connectionDataBuffer[s]['index'] >= BUFFER_SIZE)):
                                connectionDataBuffer[s]['index'] = 0
                                data1 = connectionDataBuffer[s]['str']

                                connectionDataBuffer[s]['str'] = ''
                                clientNumStr = data1.split(",")
                                # print clientNumStr
                                clientData = [0] * len(clientNumStr)
                                i = 0
                                for i in range(len(clientNumStr)):
                                    try:
                                        clientData[i] = int(clientNumStr[i])
                                    except:
                                        clientData[i] = 0



                                for i in range(len(appVariables.clientListFcn)):
                                    if appVariables.clientListFcn[i]['connection'] == s:
                                        appVariables.clientList[i]['in'] = data1
                                        appVariables.clientList[i]['ip'] = s.getpeername()[0]

                                        appVariables.clientInfoList[i]['ip'] = s.getpeername()[0]

                                        if len(clientData) > 2:
                                            if clientData[0] == 100:
                                                # msg = "[TCPServerThread] code 100: " + str(clientData[1]) + ", " + str(clientData[2])
                                                # if not appVariables.qDebug1.full():
                                                #     appVariables.qDebug1.put(msg)
                                                appVariables.clientList[i]['id'] = clientData[1]
                                                appVariables.clientList[i]['type'] = clientData[2]

                                                appVariables.clientInfoList[i]['id'] = clientData[1]
                                                appVariables.clientInfoList[i]['type'] = clientData[2]

                                            else:
                                                appVariables.clientList[i]['data'] = clientData

                                        if clientData[0] != 100:
                                            # use only actual data
                                            if not appVariables.clientListFcn[i]['q_in'].full():
                                                appVariables.clientListFcn[i]['q_in'].put(
                                                    {'str': data1, 'data': clientData})

                                        appVariables.clientListFcn[i]['t0'] = t1

                                        appVariables.clientList[i]['counter_rx'] = appVariables.clientList[i][
                                                                                       'counter_rx'] + 1

                                        try:
                                            if (not appVariables.qTCPIn.full()) and (appVariables.clientList[i]['data'][0]!=211):
                                                appVariables.qTCPIn.put(
                                                    '[' + str(appVariables.clientList[i]['id']) + '] ' + data1)
                                        except:
                                            pass

                                        break
                    except:
                        appVariables.print_exception("[TCPServerThread] read exception: " + ', at socket: ' + str(
                            s) + ' closing socket: ')

                        outputs.remove(s)
                        inputs.remove(s)

                        # Remove connection data from list
                        del connectionDataBuffer[s]
                        for i in range(len(appVariables.clientListFcn)):
                            if appVariables.clientListFcn[i]['connection'] == s:
                                del appVariables.clientListFcn[i]
                                del appVariables.clientList[i]
                                break
                        s.close()

            # Handle outputs
            for s in writable:
                for i in range(len(appVariables.clientListFcn)):
                    if appVariables.clientListFcn[i]['connection'] == s:
                        try:
                            # handle external data
                            if not appVariables.clientListFcn[i]['q_out'].empty():
                                new_data = appVariables.clientListFcn[i]['q_out'].get(block=False)
                                appVariables.clientList[i]['counter_tx'] = appVariables.clientList[i]['counter_tx'] + 1
                                new_data = appVariables.add_checksum(new_data)
                                new_data += '\n'
                                s.send(new_data)

                                try:
                                    if (not appVariables.qTCPOut.full()) and (appVariables.clientList[i]['data'][0] != 211):
                                        appVariables.qTCPOut.put('[' + str(appVariables.clientList[i]['id']) + '] ' + new_data)
                                except:
                                    pass
                        except:
                            appVariables.print_exception("[TCPServerThread] write exception: " + ', at socket: ' + str(
                                s) + ' closing socket: ')

                            outputs.remove(s)
                            inputs.remove(s)
                            s.close()
                            # Remove connection data from list
                            del connectionDataBuffer[s]
                            for i in range(len(appVariables.clientListFcn)):
                                if appVariables.clientListFcn[i]['connection'] == s:
                                    del appVariables.clientListFcn[i]
                                    del appVariables.clientList[i]
                                    break
                            break

            # Handle "exceptional conditions"
            for s in exceptional:

                msg = "[TCPServerThread] " + 'handling exceptional condition' + ', at socket: ' + str(s)
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)

                # Stop listening for input on the connection
                inputs.remove(s)
                outputs.remove(s)
                s.close()
                # Remove message queue
                del connectionDataBuffer[s]
                for i in range(len(appVariables.clientListFcn)):
                    if appVariables.clientListFcn[i]['connection'] == s:
                        del appVariables.clientListFcn[i]
                        del appVariables.clientList[i]
                        break
            # # Handle timeout
            # if not (readable or writable or exceptional):
            #     print >> sys.stderr, '  timed out, do some other work here'
            #     continue

            # Handle timeouts (received data)

            for i in range(len(appVariables.clientListFcn)):
                s = appVariables.clientListFcn[i]['connection']
                if s not in readable and (t1 - appVariables.clientListFcn[i]['t0']) > 30:
                    appVariables.clientListFcn[i]['t0'] = t1
                    msg = "[TCPServerThread] " + ' no data, ' + ', at socket: ' + str(s) + ', socket closed'
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)

                    inputs.remove(s)
                    outputs.remove(s)
                    s.close()
                    # Remove message queue
                    del connectionDataBuffer[s]
                    del appVariables.clientListFcn[i]
                    del appVariables.clientList[i]
                    break
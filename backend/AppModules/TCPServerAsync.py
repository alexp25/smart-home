import datetime
import socketserver
import appVariables
import time
import copy
from multiprocessing import Queue

class TCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            # print "Connection from: %s" % str(self.client_address)
            # request_msg = self.rfile.readline(1024)
            # msg = "[simple_tcp_server] "+str(request_msg)
            # if not appVariables.qDebug1.full():
            #     appVariables.qDebug1.put(msg)
            # self.wfile.write('211,\n')
            # self.wfile.flush()
            self.request.setblocking(0)
            t0=time.time()
            self.data=''
            self.index=0

            msg = "[TCPRequestHandler] new connection at " + str(self.client_address[0])
            if not appVariables.qDebug1.full():
                appVariables.qDebug1.put(msg)

            # update client list with connected client
            clientInList = False
            for i in range(len(appVariables.clientListFcn)):
                if appVariables.clientList[i]['ip'] == self.client_address[0]:
                    clientInList = True
                    appVariables.clientList[i]['id'] = 0
                    appVariables.clientListFcn[i]['t0'] = t0
                    appVariables.clientListFcn[i]['t0_polling'] = t0
                    appVariables.clientListFcn[i]['t0_log'] = t0
                    break

            if not clientInList:
                msg = "[TCPRequestHandler] add client "
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)

                newClientFcn = copy.deepcopy(appVariables.clientModelFcn)
                newClientFcn['q_in'] = Queue(maxsize=10)
                newClientFcn['q_out'] = Queue(maxsize=10)
                newClientFcn['t0'] = t0
                newClientFcn['t0_polling'] = t0
                newClientFcn['t0_log'] = t0
                appVariables.clientListFcn.append(newClientFcn)
                newClient = copy.deepcopy(appVariables.clientModel)
                newClient['ip'] = self.client_address[0]
                newClient['counter_rx'] = 0
                newClient['counter_tx'] = 0
                appVariables.clientList.append(newClient)
                appVariables.clientInfoList.append({'id': 0, 'ip': 0, 'type': 0})
            else:
                msg = "[TCPRequestHandler] update client "
                if not appVariables.qDebug1.full():
                    appVariables.qDebug1.put(msg)

            while 1:
                time.sleep(0.01)
                t1=time.time()

                try:
                    self.data = self.request.recv(1024).decode()
                except:
                    self.data = None

                if self.data is not None:

                    # self.data = self.data.strip()

                    # msg = "[TCPServerThread] recv " + str(self.client_address[0]) + ': ' + str(self.data)
                    # if not appVariables.qDebug1.full():
                    #     appVariables.qDebug1.put(msg)

                    # parse client data

                    # print(self.data)
                    clientNumStr = self.data.split(",")
                    # print clientNumStr
                    clientData = [0] * len(clientNumStr)
                    i = 0
                    for i in range(len(clientNumStr)):
                        try:
                            clientData[i] = int(clientNumStr[i])
                        except:
                            clientData[i] = 0

                    # update client list

                    for i in range(len(appVariables.clientListFcn)):
                        if appVariables.clientList[i]['ip'] == self.client_address[0]:
                            appVariables.clientList[i]['in'] = self.data
                            appVariables.clientInfoList[i]['ip'] = self.client_address[0]

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
                                        {'str': self.data, 'data': clientData})

                            appVariables.clientListFcn[i]['t0'] = t1
                            appVariables.clientList[i]['counter_rx'] = appVariables.clientList[i][
                                                                           'counter_rx'] + 1

                            try:
                                if (not appVariables.qTCPIn.full()) and (appVariables.clientList[i]['data'][0] != 211):
                                    appVariables.qTCPIn.put('[' + str(appVariables.clientList[i]['id']) + '] ' + self.data)
                            except:
                                pass

                    self.data=''
                # end while
                # handle sending data
                for i in range(len(appVariables.clientList)):
                    if appVariables.clientList[i]['ip'] == self.client_address[0]:
                        # handle external data
                        if not appVariables.clientListFcn[i]['q_out'].empty():
                            new_data = appVariables.clientListFcn[i]['q_out'].get(block=False)
                            appVariables.clientList[i]['counter_tx'] = appVariables.clientList[i]['counter_tx'] + 1
                            new_data = appVariables.add_checksum(new_data)
                            new_data += '\n'
                            self.request.send(new_data.encode())
                            try:
                                if (not appVariables.qTCPOut.full()) and (appVariables.clientList[i]['data'][0] != 211):
                                    appVariables.qTCPOut.put('[' + str(appVariables.clientList[i]['id']) + '] ' + new_data)
                            except:
                                pass

                # handle timeouts (received data)
                expired=False
                for i in range(len(appVariables.clientList)):
                    if appVariables.clientList[i]['ip'] == self.client_address[0]:
                        if (t1 - appVariables.clientListFcn[i]['t0']) > 10:
                            appVariables.clientListFcn[i]['t0'] = t1
                            msg = "[TCPRequestHandler] " + ' no data at  ' + str(self.client_address[0]) + '. socket closed'
                            if not appVariables.qDebug1.full():
                                appVariables.qDebug1.put(msg)

                            del appVariables.clientListFcn[i]
                            del appVariables.clientList[i]
                            del appVariables.clientInfoList[i]
                            expired = True
                        break

                if expired:
                    break

        except:
            appVariables.print_exception("[TCPRequestHandler] exception. closing socket at " + self.client_address[0])


def simple_tcp_server():
    msg = "[simple_tcp_server] start"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    tcp_server = socketserver.ThreadingTCPServer(
        ("0.0.0.0", 8050),
        RequestHandlerClass=TCPRequestHandler,
        bind_and_activate=False)

    tcp_server.allow_reuse_address = True
    tcp_server.server_bind()
    tcp_server.server_activate()

    tcp_server.serve_forever()

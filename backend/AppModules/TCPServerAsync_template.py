import datetime
import socketserver
import appVariables
import time

class TCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            self.request.setblocking(0)
            t0=time.time()
            self.data=''
            self.index=0
            while 1:
                time.sleep(0.01)
                t1=time.time()
                # self.data = self.request.recv(1024)
                # self.c = self.request.recv(1)
                while 1:
                    try:
                        self.c = self.rfile.read(1)
                    except:
                        break

                    self.data += self.c
                    self.index += 1
                    if ((self.c == '\n') or (self.index >= 50)):
                        self.index = 0
                        # self.data = self.data.strip()
                        msg = "[simple_tcp_server] recv " + str(self.client_address[0]) + ': ' + str(self.data)
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)

                        self.data=''

                if t1-t0>=1:
                    t0=t1
                    msg = "[simple_tcp_server] send "
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)
                    self.request.send("100,\n")

        except:
            appVariables.print_exception("[TCPRequestHandler]")


def simple_tcp_server():
    msg = "[simple_tcp_server] start"
    if not appVariables.qDebug1.full():
        appVariables.qDebug1.put(msg)

    tcp_server = socketserver.ThreadingTCPServer(
        ("0.0.0.0", 8050),
        RequestHandlerClass=TCPRequestHandler,
        bind_and_activate=False)
    # tcp_server.setblocking(0)

    tcp_server.allow_reuse_address = True
    tcp_server.server_bind()
    tcp_server.server_activate()

    tcp_server.serve_forever()

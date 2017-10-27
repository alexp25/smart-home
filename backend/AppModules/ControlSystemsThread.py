import time
import appVariables
from threading import Thread
import sys
import json

def write_virtual_nodes(virtualNodeList):
    with open('config/virtual_nodes.json', 'w') as f:
        f.write(json.dumps(virtualNodeList, sort_keys=True, indent=4, separators=(',', ': ')))

class ControlSystemsThread(Thread):
    def run(self):
        msg = "[ControlSystemsThread] " + 'running'
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)

        while True:
            time.sleep(0.5)
            # msg = "[ControlSystemsThread] " + 'running'
            # if not appVariables.qDebug1.full():
            #     appVariables.qDebug1.put(msg)
            # print('vnodes:')
            # print(len(appVariables.virtualNodeList))
            for knode in range(len(appVariables.virtualNodeList)):
                vnode = appVariables.virtualNodeList[knode]
                # relay controller
                try:
                    # check for parameter changes
                    if not appVariables.virtualNodeListFcn[knode]['q_out'].empty():
                        msg = "[ControlSystemsThread] " + 'parameter change'
                        if not appVariables.qDebug1.full():
                            appVariables.qDebug1.put(msg)
                        cmdString=appVariables.virtualNodeListFcn[knode]['q_out'].get(block=False)
                        cmdStringArray=cmdString.split(",")
                        cmdArray = [0] * len(cmdStringArray)
                        for i in range(len(cmdStringArray)):
                            try:
                                cmdArray[i] = int(cmdStringArray[i])
                            except:
                                cmdArray[i] = 0
                        cmd = cmdArray[0]
                        # execute received commands (user)
                        # get index of command
                        indexofcmd=-1
                        for icmd in range(len(vnode['sdata'])):
                            if cmd == vnode['sdata'][icmd]['id']:
                                indexofcmd=icmd
                                break

                        if indexofcmd!=-1:
                            if cmd>1 and cmd <= 100:
                                # value
                                appVariables.virtualNodeList[knode]['sdata'][indexofcmd]['value'] = cmdArray[1]
                            elif cmd>=101 and cmd <= 200:
                                # binary toggle
                                appVariables.virtualNodeList[knode]['sdata'][indexofcmd]['value'] = bool(appVariables.virtualNodeList[knode]['sdata'][indexofcmd]['value'])^(True)
                            elif cmd > 201 and cmd <= 300:
                                # binary trigger commands
                                pass
                            elif cmd >= 301 and cmd <= 400:
                                # enable commands
                                appVariables.virtualNodeList[knode]['sdata'][indexofcmd]['value'] = 1
                            elif cmd >= 401 and cmd <= 500:
                                # disable commands
                                appVariables.virtualNodeList[knode]['sdata'][indexofcmd]['value'] = 0
                        else:
                            # special cmd
                            if cmd==1:
                                # id
                                appVariables.virtualNodeList[knode]['id'] = cmdArray[1]
                            if cmd == 201:
                                # save
                                msg = "[ControlSystemsThread] " + 'save'
                                if not appVariables.qDebug1.full():
                                    appVariables.qDebug1.put(msg)
                                write_virtual_nodes(appVariables.virtualNodeList)


                    if vnode['type'] == 1001:
                        # I/O relay
                        input = None
                        output = None

                        input_node = 0
                        input_channel = 0
                        output_node=0
                        output_channel=0
                        id_input=0
                        id_output=0
                        lo_thd=0
                        hi_thd=0
                        inverted=False
                        enabled=False

                        for icmd in range(len(vnode['sdata'])):
                            val = vnode['sdata'][icmd]['value']
                            if vnode['sdata'][icmd]['id']==10:
                                input_node = val
                            elif vnode['sdata'][icmd]['id']==11:
                                input_channel = val
                            elif vnode['sdata'][icmd]['id']==20:
                                output_node = val
                            elif vnode['sdata'][icmd]['id']==21:
                                output_channel = val
                            elif vnode['sdata'][icmd]['id']==2:
                                id_input = icmd
                            elif vnode['sdata'][icmd]['id']==3:
                                id_output = icmd
                            elif vnode['sdata'][icmd]['id']==4:
                                lo_thd = val
                            elif vnode['sdata'][icmd]['id']==5:
                                hi_thd = val
                            elif vnode['sdata'][icmd]['id'] == 101:
                                enabled = val
                            elif vnode['sdata'][icmd]['id']==102:
                                inverted = val

                        # print(id_input)
                        # print(vnode['sdata'])
                        # read input
                        for client in appVariables.clientList:
                            if client['id']==input_node:
                                channelid=input_channel
                                if channelid < len(client['data']):
                                    input=client['data'][channelid]
                                    vnode['sdata'][id_input]['value']=input
                                break

                        # calculate output
                        if input is not None:
                            # control law
                            if input < lo_thd:
                                if inverted:
                                    output = 0
                                else:
                                    output = 1
                                vnode['sdata'][id_output]['value'] = output
                            elif input > hi_thd:
                                if inverted:
                                    output = 1
                                else:
                                    output = 0
                                vnode['sdata'][id_output]['value'] = output

                        # update output, if controller is active (enabled)
                        if enabled and (output is not None):
                            for i in range(len(appVariables.clientList)):
                                if appVariables.clientList[i]['id'] == output_node:
                                    channelid = output_channel
                                    if not appVariables.clientListFcn[i]['q_out'].full():
                                        # appVariables.clientListFcn[i]['q_out'].put("51,"+str(channelid)+","+str(output)+",\n")
                                        new_data="51,"+str(output)
                                        new_data = appVariables.add_checksum(new_data)
                                        appVariables.clientListFcn[i]['q_out'].put(new_data)
                                    break
                except:
                    exc_type, exc_value = sys.exc_info()[:2]
                    exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
                    em1 = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
                    msg = "[ControlSystemsThread] " + em1 + ', ' + exceptionMessage
                    if not appVariables.qDebug1.full():
                        appVariables.qDebug1.put(msg)


                    # print (output)

        msg = "[ControlSystemsThread] " + 'stopped'
        if not appVariables.qDebug1.full():
            appVariables.qDebug1.put(msg)
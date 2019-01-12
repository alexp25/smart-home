import time
import sys
import json
import sqlite3
import appVariables
# import mysql.connector


def DatabaseManagerProcess(qDatabaseIn, qDatabaseOut, qDebug1, dbfile):

    def connect():
        # init connection
        # conn = mysql.connector.connect(
        #     host="localhost",
        #     user="pi",
        #     passwd="raspberry",
        #     database="smarthome"
        # )
        #
        # curs = conn.cursor()

        conn = sqlite3.connect(dbfile, timeout=appVariables.db_timeout)

        conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
        curs = conn.cursor()

        return(conn, curs)

    stop_flag = 0

    while True:
        time.sleep(0.1)
        if stop_flag:
            break
        if not qDatabaseIn.empty():
            try:
                data = qDatabaseIn.get(False)

                requestId = data[0]
                if requestId == -1:
                    stop_flag = 1
                    break

                sqlstr = data[1]
                params = data[2]

                msg = "[DatabaseManagerProcess] " + requestId + " - " + str(sqlstr) + ' - ' + str(params)
                if qDebug1.full()==False:
                    qDebug1.put(msg)

                conn, curs = connect()

                if params is None:
                    params = ()

                curs.execute(sqlstr, params)
                # commit the changes

                data = curs.fetchall()

                if len(data) == 0:
                    data = False
                else:
                    data = json.dumps([dict(ix) for ix in data]) #CREATE JSON

                qDatabaseOut.put((requestId, data))

                msg = "[DatabaseManagerProcess] " + "commit"
                if not qDebug1.full():
                    qDebug1.put(msg)

                conn.commit()
                conn.close()

            except:
                exc_type, exc_value = sys.exc_info()[:2]
                exceptionMessage = str(exc_type.__name__) + ': ' + str(exc_value)
                msg = "[DatabaseManagerProcess] " + exceptionMessage
                if not qDebug1.full():
                    qDebug1.put(msg)
                continue
#!/usr/bin/env python

import sqlite3
import json
import datetime

conn=sqlite3.connect('mydatabase.db')
conn.row_factory = sqlite3.Row 
curs=conn.cursor()


print "\nEntire database contents:\n"
for row in curs.execute("SELECT * FROM Users"):
    print row[0]



print "\nDatabase entries for the user:\n"
for row in curs.execute("SELECT * FROM Users WHERE Username='alex'"):
    print row[0]

x='alex'
print "\nDatabase entries for the user x (variable):\n"
for row in curs.execute("SELECT * FROM Users WHERE Username=(?)",(x,)):
    print row

def add_user (user,passwd):
    # I used triple quotes so that I could break this string into
    # two lines for formatting purposes
    curs.execute("""INSERT INTO Users values(NULL, (?), (?))""", (user,passwd))

    # commit the changes
    conn.commit()

    
##add_user('gibou2','jack2bou')

print "\nEntire database contents:\n"
for row in curs.execute("SELECT * FROM Users"):
    print row[0] 

##for row in curs.execute("SELECT * FROM Sensors ORDER BY timestamp ASC LIMIT 50"):
##    print row
    
##for row in curs.execute("SELECT * FROM (SELECT * FROM Sensors ORDER BY timestamp DESC LIMIT 50) ORDER BY timestamp ASC"):
##    print row

print '\ntable names:\n'
for row in curs.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print row[0]


print '\nget control data:\n'
sid = 2
    

curs.execute("SELECT * FROM Control WHERE SensorId = (?) ORDER BY Timestamp ASC",(str(sid)))
data = curs.fetchall()

data = json.dumps([dict(ix) for ix in data]) #CREATE JSON  
print data

print '\nget avg:\n'
sid = 2
date1 = datetime.datetime.now()
startdate = date1 - datetime.timedelta(hours=4)
enddate   = date1

print [startdate, enddate]

curs.execute("SELECT avg(data1) as avg_hum FROM (SELECT data1 FROM SensorData WHERE SensorId = (?) AND timestamp BETWEEN (?) AND (?) ORDER BY timestamp ASC)",(str(sid),startdate,enddate))             
##curs.execute("SELECT * FROM SensorData WHERE SensorId = (?) ORDER BY timestamp ASC",(str(sid)))
data = curs.fetchall()
data = data[0]
avg_hum = data[0]
##print int(avg_hum)

timestamp = datetime.datetime.now()
watering_time=0

curs.execute("INSERT INTO Control values(NULL, (?), (?), (?), (?))", (sid,timestamp,watering_time,avg_hum))
conn.commit()

conn.close()

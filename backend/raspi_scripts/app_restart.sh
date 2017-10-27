#!/bin/sh
for KILLPID in `ps aux | grep 'python' | grep 'server01' | awk ' { print $2;}'`; do 
  kill -9 $KILLPID;
done

sleep 5

cd /
cd home/pi/Desktop/smart_home
sudo python server01.py
cd /

@ECHO ON
CD ..\frontend
START lineman run
START atom .
::START python "server01.py"
START /d "C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2016.2.2\bin\" pycharm64.exe "%~dp0..\backend\server01.py"
START chrome "http://localhost:8001"
pause
EXIT /B 0
@ECHO OFF
CD ..

::build app with lineman
CD frontend
START /W lineman build

::copy other required files which are not copied by lineman
CD ..
START /W robocopy frontend\dist\css backend\dist\css /s /e
START /W robocopy frontend\dist\js backend\dist\js /s /e
START /W robocopy frontend\dist\templates backend\dist\templates /s /e

pause
EXIT /B 0

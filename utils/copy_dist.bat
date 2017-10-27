@ECHO OFF
CD ..

START /W robocopy frontend\dist\css backend\dist\css /s /e
START /W robocopy frontend\dist\js backend\dist\js /s /e
START /W robocopy frontend\dist\templates backend\dist\templates /s /e
START /W robocopy frontend\dist\libs backend\dist\libs /s /e
START /W robocopy frontend\dist\fonts backend\dist\fonts /s /e

pause
EXIT /B 0

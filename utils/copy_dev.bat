@ECHO ON
CD ..

START /W robocopy frontend\app\templates backend\dist\templates /s /e

pause
EXIT /B 0


@ECHO ON
CD ..

START /W robocopy frontend\dist\index.html backend\dist\index.html

pause
EXIT /B 0

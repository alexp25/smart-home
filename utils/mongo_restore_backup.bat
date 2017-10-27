CD /D "C:\Program Files\MongoDB\Server\3.4\bin"
mongorestore --drop -d mydb "%~dp0..\backup\mydb"
::mongorestore --help
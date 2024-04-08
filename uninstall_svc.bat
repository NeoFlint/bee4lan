@echo off
REM uninstall the bee4lan service.
REM ------------------------------

set server_path=R:\bee4lan
set local_path="C:\Program Files\bee4lan"

REM uninstall the service
CD /D %local_path%
CALL down.bat

echo Waiting for pythonservice ending processes...
PING -n 5 127.0.0.1>nul 
echo. 

REM clean the space
cd..
RMDIR /S %local_path%
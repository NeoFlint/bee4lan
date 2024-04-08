@echo off
REM Installs bee4lan service.
REM -------------------------

set server_path=R:\bee4lan
set local_path="C:\Program Files\bee4lan"

REM copy service files 
xcopy %server_path%\install\*.* %local_path%\*.*
mkdir %local_path%\history\
echo.

REM install python and pywin32 extension 
REM ...comment it out, if you already have python 2.7.11 installed
msiexec /i python-2.7.11.msi
pywin32-220.win32-py2.7.exe

REM register pythonservice
REM ...important for the service to work
CD /D "C:\Python27\Lib\site-packages\win32\"
pythonservice.exe /register && echo Pythonservice registered SUCCESSFULLY.
echo.

REM install svc
REM ...comment it out, if you want to install the service manually - see batch files
CD /D %local_path%
CALL up.bat

REM run hostinfo
REM ...important for the server application to be able to control this PC remutely 
%server_path%\hostinfo.py > %server_path%\hosts\%computername%.txt


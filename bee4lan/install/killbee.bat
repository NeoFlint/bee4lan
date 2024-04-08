@echo off
REM trochu nasilnejsi ukonceni neposlusne sluzby bee4lan a jeji odstraneni ze sluzeb

sc delete bee4lan
TASKKILL /F /IM pythonservice.exe
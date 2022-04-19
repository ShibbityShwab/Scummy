:loop
@echo off
py getLogs.py
timeout /t 300 /nobreak
exit0
goto :loop
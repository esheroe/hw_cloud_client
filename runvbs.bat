@echo off

:start
echo start!
start runtrain.bat
choice /t 70 /d y /n >nul

goto start
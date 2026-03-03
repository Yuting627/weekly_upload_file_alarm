@echo off
chcp 65001 >nul
echo Running reminder script (test)...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0run_weekly_reminder.ps1"
pause

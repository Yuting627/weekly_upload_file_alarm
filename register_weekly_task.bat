@echo off
chcp 65001 >nul
echo Registering weekly Monday 15:00 reminder task...
echo.

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%run_weekly_reminder.ps1"
set "TASK_NAME=WeeklyReleaseTrackReminder"

if not exist "%SCRIPT_PATH%" (
    echo Error: run_weekly_reminder.ps1 not found.
    pause
    exit /b 1
)

schtasks /Query /TN "%TASK_NAME%" >nul 2>&1 && (
    echo Removing existing task...
    schtasks /Delete /TN "%TASK_NAME%" /F
)

schtasks /Create /TN "%TASK_NAME%" /TR "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%SCRIPT_PATH%\"" /SC WEEKLY /D MON /ST 15:00 /F

if %ERRORLEVEL% equ 0 (
    echo.
    echo Task created successfully.
    echo Name: %TASK_NAME%
    echo Schedule: Every Monday 15:00
    echo Actions: Popup + open folder + open Box in Chrome
    echo.
    echo You can view or edit it in Task Scheduler.
) else (
    echo Failed. Try running this script as Administrator.
)

pause

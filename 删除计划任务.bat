@echo off
chcp 65001 >nul
schtasks /Delete /TN "WeeklyReleaseTrackReminder" /F
echo Task removed.
pause

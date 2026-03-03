# Weekly release track reminder
# 1. Show Qt dialog (QSS styled); 2. If user clicks Open: open folder + Chrome

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "reminder_dialog.py"
$pythonExe = "python"

if (-not (Test-Path $pyScript)) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("reminder_dialog.py not found.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    exit 1
}

& $pythonExe $pyScript
$dialogExit = $LASTEXITCODE

if ($dialogExit -ne 0) { exit $dialogExit }

# User clicked Open: open folder and Box link
$folderPath = "E:\du\WR\weekly_new_release_track"
if (Test-Path $folderPath) {
    Start-Process explorer.exe -ArgumentList $folderPath
}
$boxUrl = "https://app.box.com/folder/359316630190?tc=collab-folder-invite-treatment-b"
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$chromeExe = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($chromeExe) {
    Start-Process $chromeExe -ArgumentList $boxUrl
} else {
    Start-Process $boxUrl
}

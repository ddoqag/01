@echo off
:: Claude Code Dynamic Status Bar
:: Universal version that works in different environments

:: Mode file path
set "MODE_FILE=%USERPROFILE%\.claude\current_mode.txt"

:: Default to Flow mode
set "STATUS_OUTPUT=🎯 Flow"

:: Try to read the first line of the mode file
if exist "%MODE_FILE%" (
    :: Use a simple read method
    for /f "usebackq delims=" %%a in ("%MODE_FILE%") do (
        set "STATUS_OUTPUT=%%a"
        goto :done_reading
    )
)

:done_reading

:: Get current directory
set "CWD=%CD%"

:: Simplify directory display
if "%CWD%"=="C:\Users\ddo\AppData\Roaming\npm" (
    set "DISPLAY_DIR=~/AppData/Roaming/npm"
) else (
    call set "DISPLAY_DIR=%%CWD:%USERPROFILE%=~%%"
)

:: Output status bar
echo %STATUS_OUTPUT% %DISPLAY_DIR%
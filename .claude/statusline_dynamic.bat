@echo off
:: Claude Code Dynamic Status Bar
:: Reads current mode from .claude/current_mode.txt

:: Try to read from mode file
if exist ".claude\current_mode.txt" (
    for /f "delims=" %%a in ('type ".claude\current_mode.txt" 2^>nul') do (
        echo %%a ~/AppData/Roaming/npm
        goto :end
    )
)

:: Default if file doesn't exist or can't be read
echo 🎯 Flow ~/AppData/Roaming/npm

:end
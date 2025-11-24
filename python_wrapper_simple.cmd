@echo off
setlocal enabledelayedexpansion

REM Try to find Python in standard locations
set "PYTHON_CMD="

REM Check Windows Apps Python first
if exist "C:\Users\ddo\AppData\Local\Microsoft\WindowsApps\python.exe" (
    set "PYTHON_CMD=C:\Users\ddo\AppData\Local\Microsoft\WindowsApps\python.exe"
)

REM Check Python314 if Windows Apps not available
if not defined PYTHON_CMD (
    if exist "C:\Users\ddo\AppData\Local\Programs\Python\Python314\python.exe" (
        set "PYTHON_CMD=C:\Users\ddo\AppData\Local\Programs\Python\Python314\python.exe"
    )
)

REM If no Python found, exit with error
if not defined PYTHON_CMD (
    echo Python not found in standard locations
    exit /b 1
)

REM Execute Python with all arguments
"%PYTHON_CMD%" %*
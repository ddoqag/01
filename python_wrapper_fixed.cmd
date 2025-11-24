@echo off
setlocal enabledelayedexpansion

REM Clear potentially interfering environment variables
set PYTHONHOME=
set PYTHONPATH=

REM Set Python environment variables
set "PYTHONHOME=C:\Users\ddo\AppData\Local\Programs\Python\Python314"
set "PYTHONPATH=C:\Users\ddo\AppData\Local\Programs\Python\Python314\Lib"
set "PATH=C:\Users\ddo\AppData\Local\Programs\Python\Python314;C:\Users\ddo\AppData\Local\Programs\Python\Python314\Scripts;%PATH%"

REM Execute Python command with arguments
"C:\Users\ddo\AppData\Local\Programs\Python\Python314\python.exe" %*
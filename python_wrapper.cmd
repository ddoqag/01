@echo off
setlocal

REM 设置Python环境变量
set "PYTHONHOME=C:\Users\ddo\AppData\Local\Python\pythoncore-3.12-64"
set "PYTHONPATH=C:\Users\ddo\AppData\Local\Python\pythoncore-3.12-64\Lib"
set "PATH=C:\Users\ddo\AppData\Local\Python\pythoncore-3.12-64;%PATH%"

REM 执行传递给脚本的Python命令
"C:\Users\ddo\AppData\Local\Python\pythoncore-3.12-64\python.exe" %*
@echo off
setlocal

REM 清理可能干扰的环境变量
set "PYTHONHOME="
set "PYTHONPATH="

REM 设置Python环境变量
set "PYTHONHOME=C:\Users\ddo\AppData\Local\Programs\Python\Python312"
set "PYTHONPATH=C:\Users\ddo\AppData\Local\Programs\Python\Python312\Lib"
set "PATH=C:\Users\ddo\AppData\Local\Programs\Python\Python312;C:\Users\ddo\AppData\Local\Programs\Python\Python312\Scripts;%PATH%"

REM 执行传递给脚本的Python命令
"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" %*
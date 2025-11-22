@echo off
setlocal
REM 清理可能干扰的环境变量
set "PYTHONHOME="
set "PYTHONPATH="

REM 测试Python基本功能
echo 测试Python 3.12.10安装...
echo.

REM 测试版本
"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" --version
if %errorlevel% neq 0 (
    echo ❌ Python版本检查失败
    pause
    exit /b 1
)

REM 测试基本模块
echo 测试基本模块...
"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" -c "import sys; print('✅ sys模块正常')"
if %errorlevel% neq 0 (
    echo ❌ sys模块测试失败
    pause
    exit /b 1
)

"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" -c "import json; print('✅ json模块正常')"
if %errorlevel% neq 0 (
    echo ❌ json模块测试失败
    pause
    exit /b 1
)

"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" -c "import encodings; print('✅ encodings模块正常')"
if %errorlevel% neq 0 (
    echo ❌ encodings模块测试失败
    pause
    exit /b 1
)

"C:\Users\ddo\AppData\Local\Programs\Python\Python312\python.exe" -c "import asyncio; print('✅ asyncio模块正常')"
if %errorlevel% neq 0 (
    echo ❌ asyncio模块测试失败
    pause
    exit /b 1
)

echo.
echo 🎉 Python 3.12.10 所有测试通过！
echo.
pause
@echo off
:: 真正动态的状态栏 - 每3秒切换一次模式

:: 获取当前时间的秒数
for /f "tokens=2 delims=:" %%a in ('time /t') do set "time_part=%%a"
if "%time_part%"=="" set "time_part=00"

:: 提取秒数
set "second=%time_part:~-1%"
if "%second%"=="" set "second=0"

:: 根据秒数决定模式（每3秒切换）
set /a "mod=%second% %% 3"

if %mod%==0 (
    echo 🎯 Flow %CD%
) else if %mod%==1 (
    echo 🔗 AgentFlow %CD%
) else (
    echo 🚀 Fusion %CD%
)
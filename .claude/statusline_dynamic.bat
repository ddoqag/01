@echo off
setlocal enabledelayedexpansion

:: 获取当前时间的秒数
for /f "tokens=2 delims=: " %%a in ('time /t') do set "current_time=%%a"
:: 如果获取失败，使用默认值
if "%current_time%"=="" set "current_time=00"

:: 提取秒数（如果有两位，取最后一位）
if "%current_time:~2,1%"=="" (
    set "second_digit=%current_time:~1,1%"
) else (
    set "second_digit=%current_time:~2,1%"
)

:: 确保是数字
set /a "digit=%second_digit% 2>nul"
if %digit% geq 10 set "digit=0"

:: 计算模式索引（0-2）
set /a "mode_index=%digit% %% 3"

:: 根据索引选择模式
if %mode_index%==0 set "mode=🎯 Flow"
if %mode_index%==1 set "mode=🔗 AgentFlow"
if %mode_index%==2 set "mode=🚀 Fusion"

:: 输出状态栏
echo %mode% ~/AppData/Roaming/npm
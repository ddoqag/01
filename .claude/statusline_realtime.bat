@echo off
setlocal enabledelayedexpansion

:: 实时状态栏脚本 - 根据Claude CLI的命令动态显示模式

:: 检查是否存在模式切换的环境变量或标记文件
if exist "%TEMP%\.claude_fusion_mode" (
    set "mode=🚀 Fusion"
    del "%TEMP%\.claude_fusion_mode" >nul 2>&1
) else if exist "%TEMP%\.claude_flow_mode" (
    set "mode=🎯 Flow"
    del "%TEMP%\.claude_flow_mode" >nul 2>&1
) else if exist "%TEMP%\.claude_agentflow_mode" (
    set "mode=🔗 AgentFlow"
    del "%TEMP%\.claude_agentflow_mode" >nul 2>&1
) else (
    :: 默认使用时间切换
    for /f "tokens=2 delims=: " %%a in ('time /t') do set "current_time=%%a"
    if "%current_time%"=="" set "current_time=00"

    set "second_digit=%current_time:~-1%"
    set /a "digit=%second_digit% 2>nul"
    if %digit% geq 10 set "digit=0"

    set /a "mode_index=%digit% %% 3"

    if %mode_index%==0 set "mode=🎯 Flow"
    if %mode_index%==1 set "mode=🔗 AgentFlow"
    if %mode_index%==2 set "mode=🚀 Fusion"
)

:: 获取当前目录
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 检查是否在用户目录下
echo %current_dir% | findstr /C:"%USERPROFILE%" >nul
if %errorlevel%==0 (
    set "display_dir=%current_dir:%USERPROFILE%=~%"
) else (
    set "display_dir=%current_dir%"
)

:: 输出状态栏
echo %mode% %display_dir%
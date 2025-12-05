@echo off
setlocal enabledelayedexpansion

:: 动态模式检测状态栏脚本
:: 通过检测最近的活动来判断当前模式

:: 检查环境变量
set "mode="

:: 方式1：检查 CLAUDE_MODE 环境变量
if defined CLAUDE_MODE (
    if /i "!CLAUDE_MODE!"=="fusion" set "mode=🚀 Fusion"
    if /i "!CLAUDE_MODE!"=="flow" set "mode=🎯 Flow"
    if /i "!CLAUDE_MODE!"=="agentflow" set "mode=🔗 AgentFlow"
)

:: 方式2：检查临时文件
if "%mode%"=="" (
    if exist "%TEMP%\.claude_mode_fusion" (
        set "mode=🚀 Fusion"
        del "%TEMP%\.claude_mode_fusion" >nul 2>&1
    ) else if exist "%TEMP%\.claude_mode_flow" (
        set "mode=🎯 Flow"
        del "%TEMP%\.claude_mode_flow" >nul 2>&1
    ) else if exist "%TEMP%\.claude_mode_agentflow" (
        set "mode=🔗 AgentFlow"
        del "%TEMP%\.claude_mode_agentflow" >nul 2>&1
    )
)

:: 方式3：检查模式状态文件
if "%mode%"=="" (
    if exist "%TEMP%\.claude_current_mode" (
        set /p mode=<"%TEMP%\.claude_current_mode"
    )
)

:: 方式4：根据时间切换（每10秒一个周期）
if "%mode%"=="" (
    for /f "tokens=2 delims=:." %%a in ('echo %time%') do set "seconds=%%a"
    if "%seconds%"=="" set "seconds=00"
    set /a "sec_num=%seconds:~-1% * 10 + %seconds:~-2,1%" 2>nul
    if %sec_num% geq 100 set "sec_num=0"
    set /a "cycle=!sec_num! %% 30"

    if !cycle! leq 9 (
        set "mode=🎯 Flow"
    ) else if !cycle! leq 19 (
        set "mode=🔗 AgentFlow"
    ) else (
        set "mode=🚀 Fusion"
    )
)

:: 获取当前目录
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 简化目录显示
set "display_dir=!current_dir:%USERPROFILE%=~!"

:: 输出状态栏
echo %mode% %display_dir%
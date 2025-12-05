@echo off
setlocal enabledelayedexpansion

:: 响应实际模式的状态栏脚本

:: 检查临时文件中的模式标记
set "mode="

:: 优先级1：检查最新的模式标记文件
if exist "%TEMP%\.claude_last_mode" (
    set /p mode=<"%TEMP%\.claude_last_mode"
) else if exist "%TEMP%\.claude_current_mode.txt" (
    set /p mode=<"%TEMP%\.claude_current_mode.txt"
) else if exist "%TEMP%\.claude_mode" (
    set /p mode=<"%TEMP%\.claude_mode"
)

:: 如果没有找到模式文件，根据最近的命令判断
if "%mode%"=="" (
    :: 默认显示为当前会话模式
    set "mode=🎯 Flow"
)

:: 获取当前目录
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 简化目录显示
set "display_dir=!current_dir:%USERPROFILE%=~!"

:: 输出状态栏
echo %mode% %display_dir%
@echo off
setlocal enabledelayedexpansion

:: 智能模式检测状态栏 - 实时检测当前使用的模式

:: 方法1：检测最近的命令或交互
set "mode=🎯 Flow"  :: 默认模式

:: 检查环境变量
if defined CLAUDE_CURRENT_MODE (
    if /i "!CLAUDE_CURRENT_MODE!"=="fusion" set "mode=🚀 Fusion"
    if /i "!CLAUDE_CURRENT_MODE!"=="flow" set "mode=🎯 Flow"
    if /i "!CLAUDE_CURRENT_MODE!"=="agentflow" set "mode=🔗 AgentFlow"
)

:: 方法2：检查临时文件中的模式标记
if exist "%TEMP%\.claude_mode.txt" (
    set /p detected_mode=<"%TEMP%\.claude_mode.txt"
    if not "!detected_mode!"=="" set "mode=!detected_mode!"
)

:: 方法3：检查系统进程或活动（如果 Claude CLI 有特定标识）
:: 这里可以根据 Claude CLI 的实际行为来检测

:: 方法4：根据最近的命令历史或交互模式
:: 如果能访问命令历史，可以分析最近的模式切换命令

:: 获取当前目录
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 简化目录显示
if "%current_dir:~0,1%"=="C" (
    set "display_dir=~/AppData/Roaming/npm"
) else (
    set "display_dir=%current_dir%"
)

:: 输出状态栏
echo %mode% %display_dir%
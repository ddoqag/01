@echo off
:: 设置 Claude 模式的工具
:: 用法: set_claude_mode.bat [flow|agentflow|fusion]

set "mode=%1"
if "%mode%"=="" (
    echo Usage: %0 [flow^|agentflow^|fusion]
    echo Current mode:
    type "%TEMP%\.claude_mode.txt" 2>nul || echo Not set
    exit /b 1
)

set "display_mode="
if /i "%mode%"=="flow" (
    set "display_mode=🎯 Flow"
) else if /i "%mode%"=="agentflow" (
    set "display_mode=🔗 AgentFlow"
) else if /i "%mode%"=="fusion" (
    set "display_mode=🚀 Fusion"
) else (
    echo Invalid mode: %mode%
    echo Use: flow, agentflow, or fusion
    exit /b 1
)

:: 保存到临时文件
echo %display_mode% > "%TEMP%\.claude_mode.txt"

:: 设置环境变量
set CLAUDE_CURRENT_MODE=%mode%

echo Mode changed to: %display_mode%
echo Status bar will update on next refresh.
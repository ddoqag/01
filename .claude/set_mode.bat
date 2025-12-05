@echo off
:: 设置当前模式的脚本
:: 用法：set_mode.bat [flow|agentflow|fusion]

set "mode=%1"
set "display_mode="

if /i "%mode%"=="flow" (
    set "display_mode=🎯 Flow"
) else if /i "%mode%"=="agentflow" (
    set "display_mode=🔗 AgentFlow"
) else if /i "%mode%"=="fusion" (
    set "display_mode=🚀 Fusion"
) else (
    echo Usage: %0 [flow^|agentflow^|fusion]
    exit /b 1
)

:: 保存到临时文件
echo %display_mode% > "%TEMP%\.claude_last_mode"
echo Mode set to: %display_mode%
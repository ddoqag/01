@echo off
:: 模式切换钩子 - 更新状态栏显示

set "mode=%1"
set "display_mode="

if /i "%mode%"=="fusion" set "display_mode=🚀 Fusion"
if /i "%mode%"=="flow" set "display_mode=🎯 Flow"
if /i "%mode%"=="agentflow" set "display_mode=🔗 AgentFlow"

:: 保存到临时文件
if defined display_mode (
    echo %display_mode% > "%TEMP%\.claude_current_mode"
    set CLAUDE_MODE=%mode%
)
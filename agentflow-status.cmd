@echo off
REM AgentFlow状态显示Windows批处理启动器
REM 自动检测环境并选择合适的显示方式

setlocal enabledelayedexpansion

REM 检测PowerShell版本，优先使用PowerShell
where pwsh >nul 2>&1
if %ERRORLEVEL% == 0 (
    REM 使用PowerShell Core
    set PS_CMD=pwsh
    goto :run_powershell
)

where powershell >nul 2>&1
if %ERRORLEVEL% == 0 (
    REM 使用Windows PowerShell
    set PS_CMD=powershell
    goto :run_powershell
)

REM 检测是否有Git Bash
where bash >nul 2>&1
if %ERRORLEVEL% == 0 (
    REM 使用Git Bash中的shell脚本
    goto :run_bash
)

echo 错误: 未找到PowerShell或Git Bash
echo 请安装PowerShell或Git for Windows
exit /b 1

:run_powershell
%PS_CMD% -ExecutionPolicy Bypass -NoProfile -File "%~dp0\.claude\agentflow-bottom-status.ps1" %*
exit /b %ERRORLEVEL%

:run_bash
bash "%~dp0\.claude\agentflow-bottom-status.sh" %*
exit /b %ERRORLEVEL%
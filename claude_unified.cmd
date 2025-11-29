@ECHO off
REM Claude Code 统一启动脚本
REM 解决别名冲突和多版本问题，确保在任何环境下都能一致启动

GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL enabledelayedexpansion
CALL :find_dp0

REM 设置标题
title Claude Code

REM 显示启动信息（仅在详细模式下）
IF "%1"=="--verbose" (
    echo [Claude Code] Starting unified launcher...
    echo [Claude Code] Script directory: %dp0%
    echo [Claude Code] Current directory: %CD%
)

REM 检查是否在正确的npm目录
IF NOT EXIST "%dp0%\node_modules\@anthropic-ai\claude-code\cli.js" (
    echo [ERROR] Claude Code CLI not found in npm directory
    echo [ERROR] Expected: %dp0%\node_modules\@anthropic-ai\claude-code\cli.js
    echo [INFO] Please ensure Claude Code is properly installed via npm
    exit /b 1
)

REM 按优先级查找Node.js可执行文件
SET "node_found="

REM 1. npm目录中的node.exe（最优先）
IF EXIST "%dp0%\node.exe" (
    SET "_prog=%dp0%\node.exe"
    SET "node_found=npm_local"
    IF "%1"=="--verbose" echo [Claude Code] Using npm-local Node.js: %_prog%
)

REM 2. 标准安装路径
IF NOT DEFINED node_found IF EXIST "C:\Program Files\nodejs\node.exe" (
    SET "_prog=C:\Program Files\nodejs\node.exe"
    SET "node_found=system"
    IF "%1"=="--verbose" echo [Claude Code] Using system Node.js: %_prog%
)

REM 3. 用户安装路径
IF NOT DEFINED node_found IF EXIST "%APPDATA%\nvm\node.exe" (
    SET "_prog=%APPDATA%\nvm\node.exe"
    SET "node_found=nvm"
    IF "%1"=="--verbose" echo [Claude Code] Using NVM Node.js: %_prog%
)

REM 4. PATH中的node命令（最后备选）
IF NOT DEFINED node_found (
    SET "_prog=node"
    SET PATHEXT=%PATHEXT:;.JS;=;%
    SET "node_found=path"
    IF "%1"=="--verbose" echo [Claude Code] Using PATH Node.js: %_prog%
)

REM 验证Node.js可用性
"%_prog%" --version >nul 2>&1
IF errorlevel 1 (
    echo [ERROR] Node.js not found or not working: %_prog%
    echo [ERROR] Please install Node.js or ensure it's in your PATH
    exit /b 1
)

REM 设置Claude Code环境变量
IF NOT DEFINED ANTHROPIC_BASE_URL (
    SET "ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic"
)
IF NOT DEFINED CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC (
    SET "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1"
)

REM 移除--verbose参数（内部使用）
SET "claude_args=%*"
SET "claude_args=!claude_args:--verbose=!"

REM 启动Claude Code CLI
IF "%1"=="--verbose" (
    echo [Claude Code] Executing: "%_prog%" "%dp0%\node_modules\@anthropic-ai\claude-code\cli.js" !claude_args!
    echo.
)

endLocal & goto #_undefined_# 2>NUL || "%_prog%"  "%dp0%\node_modules\@anthropic-ai\claude-code\cli.js" !claude_args!

REM 显示错误信息（如果有的话）
IF errorlevel 1 (
    echo.
    echo [ERROR] Claude Code failed to start
    echo [INFO] Check the error message above for details
    exit /b 1
)

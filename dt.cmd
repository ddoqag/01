@echo off
REM DeepSeek Token 管理脚本
REM 动态管理和配置Token

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo DeepSeek Token 管理工具
    echo.
    echo 使用方法:
    echo   dt status              - 查看Token状态
    echo   dt auto                - 自动配置最佳Token
    echo   dt get                 - 获取当前Token
    echo   dt update [token]      - 更新Token
    echo   dt test                - 测试Token有效性
    echo.
    echo 示例:
    echo   dt status              - 检查所有Token来源状态
    echo   dt auto                - 自动从DZH系统获取Token
    echo   dt test                - 测试当前Token是否可用
    goto :eof
)

set COMMAND=%~1
set TOKEN=%~2

if "%COMMAND%"=="status" (
    echo 📊 Token状态检查...
    python "%~dp0deepseek_token_manager.py" status
    goto :eof
)

if "%COMMAND%"=="auto" (
    echo 🔄 自动配置Token...
    python "%~dp0deepseek_token_manager.py" auto
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Token配置成功!
        echo.
        echo 现在可以测试:
        echo   ds ask "hello"
        echo   或直接对话: 请用DeepSeek回答一个问题
    )
    goto :eof
)

if "%COMMAND%"=="get" (
    python "%~dp0deepseek_token_manager.py" get
    goto :eof
)

if "%COMMAND%"=="update" (
    if "%TOKEN%"=="" (
        echo ❌ 请提供Token值
        echo 使用方法: dt update your_token_here
        goto :eof
    )
    echo 🔧 更新Token...
    python "%~dp0deepseek_token_manager.py" update --token "%TOKEN%"
    goto :eof
)

if "%COMMAND%"=="test" (
    echo 🧪 测试Token有效性...
    python "%~dp0deepseek_helper.py" ask "hello"
    goto :eof
)

echo ❌ 未知命令: %COMMAND%
echo 使用 dt 查看帮助
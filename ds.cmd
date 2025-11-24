@echo off
REM DeepSeek 简洁调用脚本
REM 使用方法: ds ask "问题" | ds analyze 000042 | ds market "分析内容"

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo DeepSeek 简洁调用工具
    echo.
    echo 使用方法:
    echo   ds ask "你的问题"           - 通用问答
    echo   ds analyze 股票代码        - 股票分析
    echo   ds market "分析内容"        - 市场分析
    echo.
    echo 示例:
    echo   ds ask "什么是量化交易？"
    echo   ds analyze 000042
    echo   ds market "今日A股走势"
    echo.
    echo 配置: 请在 settings.local.json 中设置 deepseek.api_key
    goto :eof
)

set COMMAND=%~1
set ARGS=%*

REM 调用Python脚本
python "%~dp0deepseek_helper.py" %ARGS%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 调用失败，请检查:
    echo   1. Python环境是否正常
    echo   2. settings.local.json 中的 deepseek.api_key 是否设置
    echo   3. 网络连接是否正常
)
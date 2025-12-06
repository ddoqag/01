@echo off
setlocal enabledelayedexpansion

:: 检查模式文件
set "mode_file=%USERPROFILE%\.claude\current_mode.txt"
set "current_mode=🎯 Flow"

if exist "%mode_file%" (
    for /f "delims=" %%a in ('type "%mode_file%" ^| findstr /v "^$" ^| findstr /v "^[[:space:]]*$"') do (
        set "current_mode=%%a"
        goto :mode_found
    )
)

:mode_found

:: 简单的字符串匹配来确定模式
echo %current_mode% | find "Flow" >nul && (
    echo 🎯 Flow %CD%
    goto :end
)

echo %current_mode% | find "AgentFlow" >nul && (
    echo 🔗 AgentFlow %CD%
    goto :end
)

echo %current_mode% | find "Fusion" >nul && (
    echo 🚀 Fusion %CD%
    goto :end
)

:: 默认输出
echo 🎯 Flow %CD%

:end
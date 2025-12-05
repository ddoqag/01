@echo off
:: 动态状态栏 - 显示当前实际模式和目录

:: 尝试从多个位置读取当前模式
set "current_mode="

:: 方法1: 尝试从当前目录的.claude文件夹读取
if exist "%CD%\.claude\current_mode.txt" (
    set /p current_mode=<"%CD%\.claude\current_mode.txt"
)

:: 方法2: 尝试从用户目录读取（如果方法1失败）
if "%current_mode%"=="" (
    if exist "%USERPROFILE%\.claude\current_mode.txt" (
        set /p current_mode=<"%USERPROFILE%\.claude\current_mode.txt"
    )
)

:: 方法3: 尝试从AppData目录读取（如果前两个都失败）
if "%current_mode%"=="" (
    if exist "%APPDATA%\npm\.claude\current_mode.txt" (
        set /p current_mode=<"%APPDATA%\npm\.claude\current_mode.txt"
    )
)

:: 如果都没有找到，使用默认模式
if "%current_mode%"=="" set "current_mode=🎯 Flow"

:: 输出状态栏 - 当前模式 + 当前目录
echo %current_mode% %CD%
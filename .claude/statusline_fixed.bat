@echo off
:: 固定显示当前实际使用模式的状态栏

:: 读取当前模式文件
if exist "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" (
    set /p mode=<"C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt"
) else (
    set "mode=🎯 Flow"
)

:: 获取当前目录
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 简化目录显示
set "display_dir=%current_dir:%USERPROFILE%=~%"

:: 输出状态栏
echo %mode% %display_dir%
@echo off
:: 简单的状态栏脚本，显示当前目录

for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 简单检查是否在用户目录下
echo %current_dir% | findstr /C:"%USERPROFILE%" >nul
if %errorlevel%==0 (
    set "display_dir=%current_dir:%USERPROFILE%=~%"
) else (
    set "display_dir=%current_dir%"
)

echo ⏵⏵ accept edits on (shift+tab to cycle) %display_dir% cd
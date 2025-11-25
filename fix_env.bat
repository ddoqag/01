@echo off
echo 修复系统环境变量...

REM 设置Node.js路径
setx NODEJS_PATH "C:\Program Files\nodejs" /M

REM 添加到系统PATH
setx PATH "%PATH%;C:\Program Files\nodejs" /M

echo 环境变量修复完成
echo 请重新启动命令提示符或PowerShell以使更改生效
pause

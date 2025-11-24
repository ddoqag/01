@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

REM 首先尝试npm目录中的node.exe
IF EXIST "%dp0%\node.exe" (
  SET "_prog=%dp0%\node.exe"
  GOTO :found_node
)

REM 然后尝试标准安装路径
IF EXIST "C:\Program Files\nodejs\node.exe" (
  SET "_prog=C:\Program Files\nodejs\node.exe"
  GOTO :found_node
)

REM 最后尝试系统PATH中的node
SET "_prog=node"
SET PATHEXT=%PATHEXT:;.JS;=;%

:found_node
endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & "%_prog%"  "%dp0%\node_modules\@anthropic-ai\claude-code\cli.js" --dangerously-skip-permissions %*
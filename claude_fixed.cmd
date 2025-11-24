@ECHO off
GOTO start
:find_dp0
SET dp0=%~dp0
EXIT /b
:start
SETLOCAL
CALL :find_dp0

REM 检查本地是否有node.exe
IF EXIST "%dp0%\node.exe" (
  SET "_prog=%dp0%\node.exe"
) ELSE (
  REM 使用系统的node命令
  SET "_prog=node"
  SET PATHEXT=%PATHEXT:;.JS;=;%
)

REM 使用全局安装的Claude Code CLI
endLocal & goto #_undefined_# 2>NUL || title %COMSPEC% & "%_prog%"  "%HOME%\.nvm\versions\node\v24.11.0\lib\node_modules\@anthropic-ai\claude-code\cli.js" %*
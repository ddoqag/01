@echo off
echo Testing statusline with different modes...

echo.
echo === Testing Flow Mode ===
echo 🎯 Flow > "%USERPROFILE%\.claude\current_mode.txt"
call "%USERPROFILE%\.claude\statusline_dynamic.bat"

echo.
echo === Testing AgentFlow Mode ===
echo 🔗 AgentFlow > "%USERPROFILE%\.claude\current_mode.txt"
call "%USERPROFILE%\.claude\statusline_dynamic.bat"

echo.
echo === Testing Fusion Mode ===
echo 🚀 Fusion > "%USERPROFILE%\.claude\current_mode.txt"
call "%USERPROFILE%\.claude\statusline_dynamic.bat"

echo.
echo === Restoring original mode ===
echo 🎯 Flow > "%USERPROFILE%\.claude\current_mode.txt"
call "%USERPROFILE%\.claude\statusline_dynamic.bat"

echo.
echo Test complete!
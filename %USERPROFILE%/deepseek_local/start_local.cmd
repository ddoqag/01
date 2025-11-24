@echo off
REM DeepSeek本地启动脚本

echo 🚀 DeepSeek本地工具启动
echo =======================

REM 设置本地路径
set LOCAL_DIR=%USERPROFILE%\deepseek_local
set DEEPSEEK_LOCAL_PATH=%LOCAL_DIR%
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

echo 📍 本地目录: %LOCAL_DIR%
echo.

REM 检查文件
echo 📋 检查本地文件:
if exist "%LOCAL_DIR%\deepseek_helper.py" (
    echo ✅ deepseek_helper.py
) else (
    echo ❌ deepseek_helper.py
)

if exist "%LOCAL_DIR%\dt.cmd" (
    echo ✅ dt.cmd
) else (
    echo ❌ dt.cmd
)

if exist "%LOCAL_DIR%\ds.cmd" (
    echo ✅ ds.cmd
) else (
    echo ❌ ds.cmd
)

echo.
echo 🎯 可用命令:
echo   dt status              - 查看Token状态
echo   dt auto                - 自动配置Token
echo   dt test                - 测试Token
echo   ds ask "问题"          - 询问DeepSeek
echo   ds analyze 股票代码     - 股票分析
echo.
echo 💬 直接对话方式:
echo   请用DeepSeek分析一下股票000042
echo   DeepSeek，解释一下量化交易
echo.
echo 🔧 配置Token:
echo   setx DEEPSEEK_CURRENT_TOKEN "your_token_here"
echo.

REM 如果有参数，执行命令
if not "%~1"=="" (
    echo 🔄 执行命令: %*
    cd /d "%LOCAL_DIR%"
    %*
)

echo.
echo ✅ 本地环境已就绪！
echo 💡 提示: 现在可以使用 dt 和 ds 命令
echo 按任意键退出...
pause > nul
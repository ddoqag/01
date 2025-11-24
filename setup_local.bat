@echo off
REM DeepSeek本地环境一键设置脚本
REM 将所有文件复制到本地并配置环境

echo 🚀 DeepSeek本地环境一键设置
echo =============================

REM 获取当前脚本目录
set SCRIPT_DIR=%~dp0
echo 📍 脚本目录: %SCRIPT_DIR%

REM 执行本地复制
echo 📁 正在复制文件到本地...
python "%SCRIPT_DIR%copy_to_local.py"

if %ERRORLEVEL% EQU 0 (
    echo ✅ 文件复制成功!

    REM 尝试找到本地目录并执行快速启动
    for %%d in (
        "%USERPROFILE%\deepseek_local"
        "C:\deepseek_tools"
        "%USERPROFILE%\AppData\Local\deepseek_tools"
    ) do (
        if exist "%%d\quick_start.bat" (
            echo 🚀 找到本地工具，启动快速配置...
            cd /d "%%d"
            call quick_start.bat dt auto
            goto :success
        )
    )

    echo ⚠️  未找到快速启动脚本，请手动执行:
    echo    copy_to_local.py
    echo    quick_start.bat

) else (
    echo ❌ 文件复制失败，请检查错误信息
    goto :end
)

:success
echo.
echo 🎉 设置完成!
echo 现在您可以使用:
echo   dt status    - 查看Token状态
echo   ds ask "问题" - 询问DeepSeek
echo.
echo 💬 或直接对话: 请用DeepSeek帮我分析股票000042

:end
echo.
echo 按任意键退出...
pause > nul
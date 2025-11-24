@echo off
REM DeepSeek简化安装脚本 - 不依赖Python
REM 使用纯批处理命令复制文件和配置环境

echo 🚀 DeepSeek简化安装
echo ===================

REM 获取当前目录
set SCRIPT_DIR=%~dp0
echo 📍 脚本目录: %SCRIPT_DIR%

REM 创建本地目录
set LOCAL_DIR=%USERPROFILE%\deepseek_local
echo 📁 创建本地目录: %LOCAL_DIR%

if not exist "%LOCAL_DIR%" (
    mkdir "%LOCAL_DIR%"
    echo ✅ 目录创建成功
) else (
    echo ✅ 目录已存在
)

REM 复制核心文件
echo.
echo 📋 复制核心文件...

set FILES_TO_COPY=deepseek_helper.py deepseek_token_manager.py deepseek_lite.py settings.local.json ds.cmd dt.cmd

for %%f in (%FILES_TO_COPY%) do (
    if exist "%SCRIPT_DIR%%%f" (
        copy /Y "%SCRIPT_DIR%%%f" "%LOCAL_DIR%\" >nul 2>&1
        if exist "%LOCAL_DIR%\%%f" (
            echo ✅ %%f
        ) else (
            echo ❌ %%f (复制失败)
        )
    ) else (
        echo ⚠️  %%f (源文件不存在)
    )
)

REM 创建简化的快速启动脚本
echo.
echo 🔧 创建启动脚本...

set QUICK_START=%LOCAL_DIR%\start_deepseek.bat
(
echo @echo off
echo echo 🚀 DeepSeek工具启动
echo echo ===================
echo.
echo REM 设置本地路径
echo set DEEPSEEK_LOCAL_PATH=%LOCAL_DIR%
echo set PATH=%%DEEPSEEK_LOCAL_PATH%%;%%PATH%%
echo.
echo echo 🎯 可用命令:
echo echo   dt status    - 查看Token状态
echo echo   ds ask "问题" - 询问DeepSeek
echo echo.
echo echo 💬 直接对话方式:
echo echo   请用DeepSeek分析一下股票000042
echo echo.
echo echo 🔧 配置Token:
echo echo   1. 设置环境变量: setx DEEPSEEK_CURRENT_TOKEN "your_token"
echo echo   2. 或编辑: settings.local.json
echo echo.
echo echo 按任意键退出...
echo pause > nul
) > "%QUICK_START%"

echo ✅ 创建启动脚本: %QUICK_START%

REM 设置环境变量（当前会话）
echo.
echo 🔧 设置环境变量...
set DEEPSEEK_LOCAL_PATH=%LOCAL_DIR%
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

REM 尝试永久设置环境变量
setx DEEPSEEK_LOCAL_PATH "%LOCAL_DIR%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 永久环境变量设置成功
) else (
    echo ⚠️  永久环境变量设置失败（仅当前会话有效）
)

REM 创建桌面快捷方式（简单版本）
echo.
echo 🖥️  创建桌面快捷方式...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_VBS=%TEMP%\create_deepseek_shortcut.vbs

(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\DeepSeek工具.bat"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%QUICK_START%"
echo oLink.WorkingDirectory = "%LOCAL_DIR%"
echo oLink.Description = "DeepSeek AI工具"
echo oLink.Save
) > "%SHORTCUT_VBS%"

cscript //nologo "%SHORTCUT_VBS%" >nul 2>&1
if exist "%DESKTOP%\DeepSeek工具.bat" (
    echo ✅ 桌面快捷方式创建成功
    del "%SHORTCUT_VBS%" >nul 2>&1
) else (
    echo ⚠️  桌面快捷方式创建失败
    del "%SHORTCUT_VBS%" >nul 2>&1
)

REM 创建配置文件
echo.
echo ⚙️  创建配置文件...

set CONFIG_FILE=%LOCAL_DIR%\installation_info.txt
(
echo DeepSeek本地安装信息
echo =====================
echo 安装时间: %date% %time%
echo 安装目录: %LOCAL_DIR%
echo 源文件目录: %SCRIPT_DIR%
echo.
echo 文件列表:
dir /b "%LOCAL_DIR%" 2>nul
echo.
echo 使用方法:
echo 1. 双击桌面 "DeepSeek工具.bat"
echo 2. 运行: %LOCAL_DIR%\start_deepseek.bat
echo 3. 或在命令行中使用 dt 和 ds 命令（需先运行 start_deepseek.bat）
echo.
echo 配置Token:
echo - 设置环境变量: setx DEEPSEEK_CURRENT_TOKEN "your_token_here"
echo - 或编辑文件: %LOCAL_DIR%\settings.local.json
) > "%CONFIG_FILE%"

echo ✅ 创建配置文件: %CONFIG_FILE%

REM 检查安装结果
echo.
echo 📊 安装结果检查:
echo ====================

if exist "%LOCAL_DIR%" (
    echo ✅ 本地目录存在
) else (
    echo ❌ 本地目录不存在
)

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

if exist "%DESKTOP%\DeepSeek工具.bat" (
    echo ✅ 桌面快捷方式
) else (
    echo ⚠️  桌面快捷方式（可选）
)

echo.
echo 🎉 简化安装完成！
echo.
echo 📁 本地目录: %LOCAL_DIR%
echo 🖥️  桌面快捷方式: %DESKTOP%\DeepSeek工具.bat
echo 🚀 启动脚本: %QUICK_START%
echo 📖 配置文件: %CONFIG_FILE%
echo.
echo 🎯 下一步操作:
echo 1. 双击桌面 "DeepSeek工具.bat"
echo 2. 配置Token（参考配置文件）
echo 3. 开始使用DeepSeek功能
echo.
echo 💡 提示: 如果需要完整功能，请确保Python环境正常后运行 install_local.cmd
echo.
echo 按任意键退出...
pause > nul
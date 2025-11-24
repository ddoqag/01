@echo off
REM DeepSeek本地环境最终安装脚本
REM 一键完成所有配置和优化

echo 🚀 DeepSeek本地环境完整安装
echo ============================

REM 检查管理员权限（可选）
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 检测到管理员权限，可以进行完整安装
) else (
    echo ⚠️  普通用户权限，进行用户级安装
)

echo.
echo 📋 安装步骤:
echo 1. 复制文件到本地目录
echo 2. 优化文件结构和路径
echo 3. 配置环境变量
echo 4. 创建快捷方式
echo 5. 测试功能
echo.

REM 步骤1: 文件复制
echo 📁 步骤1: 复制文件到本地...
python copy_to_local.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 文件复制失败，安装中止
    goto :error
)

REM 步骤2: 查找本地目录
echo 🔍 步骤2: 查找本地目录...
for %%d in (
    "%USERPROFILE%\deepseek_local"
    "C:\deepseek_tools"
    "%USERPROFILE%\AppData\Local\deepseek_tools"
) do (
    if exist "%%d\local_config.json" (
        set LOCAL_DIR=%%d
        echo ✅ 找到本地目录: %%d
        goto :found_local
    )
)

echo ❌ 未找到本地目录，安装失败
goto :error

:found_local

REM 步骤3: 环境变量配置
echo 🔧 步骤3: 配置环境变量...

REM 临时设置
set DEEPSEEK_LOCAL_PATH=%LOCAL_DIR%
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

REM 永久设置（用户级）
setx DEEPSEEK_LOCAL_PATH "%LOCAL_DIR%" >nul 2>&1

REM 添加到用户PATH（如果需要）
setx PATH "%LOCAL_DIR%;%PATH%" >nul 2>&1

echo ✅ 环境变量配置完成

REM 步骤4: 创建桌面快捷方式
echo 🖥️  步骤4: 创建快捷方式...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\DeepSeek工具.lnk

REM 使用PowerShell创建快捷方式
powershell -Command "
$WshShell = New-Object -comObject WScript.Shell;
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%');
$Shortcut.TargetPath = '%LOCAL_DIR%\\quick_start.cmd';
$Shortcut.WorkingDirectory = '%LOCAL_DIR%';
$Shortcut.Description = 'DeepSeek AI工具快速启动';
$Shortcut.Save();
" >nul 2>&1

if exist "%SHORTCUT%" (
    echo ✅ 桌面快捷方式创建成功
) else (
    echo ⚠️  桌面快捷方式创建失败
)

REM 步骤5: 创建开始菜单快捷方式
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
set MENU_SHORTCUT=%START_MENU%\DeepSeek工具.lnk

powershell -Command "
$WshShell = New-Object -comObject WScript.Shell;
$Shortcut = $WshShell.CreateShortcut('%MENU_SHORTCUT%');
$Shortcut.TargetPath = '%LOCAL_DIR%\\quick_start.cmd';
$Shortcut.WorkingDirectory = '%LOCAL_DIR%';
$Shortcut.Description = 'DeepSeek AI工具';
$Shortcut.Save();
" >nul 2>&1

if exist "%MENU_SHORTCUT%" (
    echo ✅ 开始菜单快捷方式创建成功
) else (
    echo ⚠️  开始菜单快捷方式创建失败
)

REM 步骤6: 初始化配置
echo 🔄 步骤6: 初始化Token配置...
cd /d "%LOCAL_DIR%"

if exist "dt.cmd" (
    echo 🔄 检查Token状态...
    dt status

    echo.
    echo 🎯 是否现在配置Token?
    echo 1. 是 - 自动配置Token
    echo 2. 否 - 稍后手动配置
    echo 3. 跳过 - 仅安装工具
    set /p config_choice=请选择 (1-3):

    if "%config_choice%"=="1" (
        echo 🔄 正在自动配置Token...
        dt auto
    ) else if "%config_choice%"=="2" (
        echo 💡 稍后可运行以下命令配置:
        echo    dt auto
    ) else (
        echo ⏭️  跳过Token配置
    )
) else (
    echo ⚠️  Token管理工具未找到
)

REM 步骤7: 功能测试
echo 🧪 步骤7: 功能测试...

if exist "deepseek_lite.py" (
    echo 🧪 测试轻量级版本...
    python deepseek_lite.py status
)

echo.
echo ✅ 安装完成摘要:
echo ====================
echo 📍 本地目录: %LOCAL_DIR%
echo 🖥️  桌面快捷方式: %SHORTCUT%
echo 📱 开始菜单: %MENU_SHORTCUT%
echo.
echo 🎯 使用方法:
echo   1. 双击桌面快捷启动
echo   2. 运行: dt auto
echo   3. 命令: ds ask "问题"
echo   4. 对话: 请用DeepSeek分析股票000042
echo.

goto :success

:error
echo.
echo ❌ 安装失败，请检查以下问题:
echo 1. Python环境是否正常
echo 2. 是否有文件写入权限
echo 3. 网络连接是否正常
echo 4. 防病毒软件是否阻止
echo.
pause
exit /b 1

:success
echo 🎉 安装成功完成!
echo.
echo 🚀 现在可以开始使用DeepSeek工具了！
echo.
echo 按任意键退出...
pause > nul
exit /b 0
@echo off
echo ========================================
echo Claude Code Windows 系统优化工具安装程序
echo ========================================
echo.

REM 检查Python安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 检测到Python安装:
python --version

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 检测到非管理员权限，某些功能可能无法正常工作
    echo 建议以管理员身份运行此安装程序
    echo.
)

echo.
echo [步骤1] 安装Python依赖包...

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo [完成] 依赖包安装成功

echo.
echo [步骤2] 创建目录结构...

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backups" mkdir backups
if not exist "reports" mkdir reports

echo [完成] 目录结构创建成功

echo.
echo [步骤3] 验证安装...

REM 测试导入主要模块
python -c "import main, config_manager, monitoring.performance_dashboard, maintenance_scheduler, compatibility_validator" 2>nul

if %errorlevel% neq 0 (
    echo [错误] 模块导入失败，请检查Python环境
    pause
    exit /b 1
)

echo [完成] 模块验证成功

echo.
echo [步骤4] 创建桌面快捷方式...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\Claude Optimizer.lnk
set SCRIPT_PATH=%cd%\run_optimizer.py

REM 使用PowerShell创建快捷方式
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '%SCRIPT_PATH% --mode all'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Description = 'Claude Code Windows 系统优化工具'; $Shortcut.Save()"

echo [完成] 桌面快捷方式创建成功

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 双击桌面快捷方式 "Claude Optimizer"
echo 2. 或在命令行中运行: python run_optimizer.py
echo.
echo 可用模式:
echo   --mode optimize      # 系统优化
echo   --mode config       # 配置管理
echo   --mode monitor      # 性能监控
echo   --mode scheduler    # 维护调度器
echo   --mode validate     # 兼容性验证
echo   --mode all          # 运行所有功能
echo.
echo 文档位置: %cd%\README.md
echo 配置文件: %cd%\configs\
echo 日志文件: %cd%\logs\
echo.
echo 按任意键退出...
pause >nul
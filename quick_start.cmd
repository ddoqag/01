@echo off
REM DeepSeek工具快速启动脚本 - 最终版本
REM 一键配置并启动DeepSeek本地环境

setlocal enabledelayedexpansion

echo 🚀 DeepSeek工具快速启动 v2.0
echo ===============================

REM 获取脚本目录
set SCRIPT_DIR=%~dp0
set ORIGINAL_DIR=%CD%

REM 检查是否已在本地目录
if exist "%SCRIPT_DIR%local_config.json" (
    echo ✅ 检测到本地配置
    set USE_LOCAL=1
) else (
    echo 🔄 需要初始化本地环境
    set USE_LOCAL=0
)

REM 步骤1: 复制文件到本地（如果需要）
if %USE_LOCAL%==0 (
    echo 📁 正在初始化本地环境...

    REM 尝试运行复制脚本
    python "%SCRIPT_DIR%copy_to_local.py" --update

    if !ERRORLEVEL! EQU 0 (
        echo ✅ 本地环境初始化成功
        set USE_LOCAL=1

        REM 查找本地目录
        for %%d in (
            "%USERPROFILE%\deepseek_local"
            "C:\deepseek_tools"
            "%USERPROFILE%\AppData\Local\deepseek_tools"
            "%SCRIPT_DIR%local_copy"
        ) do (
            if exist "%%d\quick_start_local.bat" (
                set LOCAL_DIR=%%d
                echo 📍 找到本地目录: %%d
                goto :found_local
            )
        )

        :found_local
    ) else (
        echo ⚠️  本地环境初始化失败，使用当前目录
        set LOCAL_DIR=%SCRIPT_DIR%
    )
) else (
    set LOCAL_DIR=%SCRIPT_DIR%
)

REM 步骤2: 设置环境变量
echo 🔧 配置环境变量...
set DEEPSEEK_LOCAL_PATH=%LOCAL_DIR%
set PATH=%DEEPSEEK_LOCAL_PATH%;%PATH%

REM 步骤3: 检查Token状态
echo.
echo 📊 检查Token状态...
cd /d "%DEEPSEEK_LOCAL_PATH%"

REM 检查是否有dt命令
if exist "dt.cmd" (
    echo ✅ 找到Token管理工具
    dt status
) else (
    echo ⚠️  未找到Token管理工具
)

REM 步骤4: 根据参数执行相应操作
if not "%~1"=="" (
    echo.
    echo 🔄 执行命令: %*

    REM 执行传入的命令
    %*

    goto :end
)

REM 步骤5: 提供交互式菜单
echo.
echo 🎯 选择操作:
echo 1. 自动配置Token (推荐)
echo 2. 测试Token
echo 3. 快速问答测试
echo 4. 查看使用帮助
echo 5. 退出
echo.
set /p choice=请选择 (1-5):

if "%choice%"=="1" (
    echo 🔄 自动配置Token...
    if exist "dt.cmd" (
        dt auto
    ) else (
        echo ❌ dt.cmd 未找到
    )
)
if "%choice%"=="2" (
    echo 🧪 测试Token...
    if exist "dt.cmd" (
        dt test
    ) else (
        echo ❌ dt.cmd 未找到
    )
)
if "%choice%"=="3" (
    echo 💬 快速测试...
    if exist "ds.cmd" (
        ds ask "你好，请简单介绍一下你自己"
    ) else (
        echo ❌ ds.cmd 未找到
    )
)
if "%choice%"=="4" (
    echo 📖 使用帮助:
    echo.
    echo 🎯 可用命令:
    echo   dt auto              - 自动配置Token
    echo   dt status            - 查看Token状态
    echo   dt test              - 测试Token
    echo   ds ask "问题"        - 询问DeepSeek
    echo   ds analyze 股票代码  - 股票分析
    echo   ds market "内容"     - 市场分析
    echo.
    echo 💬 直接对话方式:
    echo   请用DeepSeek分析一下股票000042
    echo   DeepSeek，解释一下量化交易
    echo.
    echo 🔧 轻量级版本:
    echo   python deepseek_lite.py ask "问题"
    echo.
    echo 📁 本地目录: %DEEPSEEK_LOCAL_PATH%
)

:end
echo.
echo 🎉 快速启动完成!
echo 💡 提示: 现在可以在任意目录使用 dt 和 ds 命令
echo 💬 或者直接对话: 请用DeepSeek帮我分析...

REM 返回原目录
cd /d "%ORIGINAL_DIR%"

REM 如果不是静默模式，等待用户输入
if "%~1"=="" (
    echo.
    echo 按任意键退出...
    pause > nul
)
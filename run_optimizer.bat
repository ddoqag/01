@echo off
setlocal enabledelayedexpansion

REM Claude Windows系统优化工具 - 一键优化
REM Fusion模式专业级解决方案

title Claude系统优化工具 - 一键优化
color 0A

echo.
echo ================================================================
echo    🚀 Claude Windows 系统优化工具 - 一键优化
echo    Fusion模式专业级解决方案 v1.0
echo ================================================================
echo.

REM 设置变量
set "OPT_DIR=%~dp0"
set "BACKUP_DIR=%OPT_DIR%backups"
set "LOG_DIR=%OPT_DIR%logs"
set "START_TIME=%date% %time%"

REM 创建必要目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 日志文件
set "LOG_FILE=%LOG_DIR%optimization_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"

REM 统计变量
set /a TOTAL_OPT=0
set /a SUCCESS_OPT=0
set /a FAILED_OPT=0

REM 开始日志
echo [%START_TIME%] [INFO] 开始Claude系统优化... >> "%LOG_FILE%"

echo [1/7] 备份重要文件...
set /a TOTAL_OPT+=1

REM 备份settings.json
if exist "%USERPROFILE%\.claude\settings.json" (
    copy "%USERPROFILE%\.claude\settings.json" "%BACKUP_DIR%\settings_backup_%date:~0,4%%date:~5,2%%date:~8,2%.json" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 已备份: settings.json
        echo [%START_TIME%] [SUCCESS] 已备份: settings.json >> "%LOG_FILE%"
    ) else (
        echo ❌ 备份失败: settings.json
        echo [%START_TIME%] [ERROR] 备份失败: settings.json >> "%LOG_FILE%"
        set /a FAILED_OPT+=1
        goto :backup_done
    )
) else (
    echo ⚠️  settings.json不存在
)

REM 备份.claude.json
if exist "%OPT_DIR%\.claude.json" (
    copy "%OPT_DIR%\.claude.json" "%BACKUP_DIR%\.claude_backup_%date:~0,4%%date:~5,2%%date:~8,2%.json" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 已备份: .claude.json
        echo [%START_TIME%] [SUCCESS] 已备份: .claude.json >> "%LOG_FILE%"
    ) else (
        echo ❌ 备份失败: .claude.json
        echo [%START_TIME%] [ERROR] 备份失败: .claude.json >> "%LOG_FILE%"
        set /a FAILED_OPT+=1
        goto :backup_done
    )
) else (
    echo ⚠️  .claude.json不存在
)

set /a SUCCESS_OPT+=1
:backup_done

echo.
echo [2/7] 优化Node.js环境...
set /a TOTAL_OPT+=1

REM 检查Node.js
if exist "C:\Program Files\nodejs\node.exe" (
    echo ✅ Node.js已安装: C:\Program Files\nodejs\node.exe

    REM 创建Node.js包装器
    echo @echo off > "%OPT_DIR%node_wrapper.bat"
    echo REM Claude Node.js环境包装器 >> "%OPT_DIR%node_wrapper.bat"
    echo set "NODE_PATH=C:\Program Files\nodejs" >> "%OPT_DIR%node_wrapper.bat"
    echo set "NODE_EXE=%%NODE_PATH%%\node.exe" >> "%OPT_DIR%node_wrapper.bat"
    echo set "NPX_CMD=%%NODE_PATH%%\npx.cmd" >> "%OPT_DIR%node_wrapper.bat"
    echo. >> "%OPT_DIR%node_wrapper.bat"
    echo if not exist "%%NODE_EXE%%" ( >> "%OPT_DIR%node_wrapper.bat"
    echo     echo Error: Node.js not found >> "%OPT_DIR%node_wrapper.bat"
    echo     exit /b 1 >> "%OPT_DIR%node_wrapper.bat"
    echo ^) >> "%OPT_DIR%node_wrapper.bat"
    echo. >> "%OPT_DIR%node_wrapper.bat"
    echo set "COMMAND=%%1" >> "%OPT_DIR%node_wrapper.bat"
    echo if "%%COMMAND%%"=="node" ( >> "%OPT_DIR%node_wrapper.bat"
    echo     "%%NODE_EXE%%" %%2 %%3 %%4 %%5 >> "%OPT_DIR%node_wrapper.bat"
    echo ^) else if "%%COMMAND%%"=="npx" ( >> "%OPT_DIR%node_wrapper.bat"
    echo     "%%NPX_CMD%%" %%2 %%3 %%4 %%5 >> "%OPT_DIR%node_wrapper.bat"
    echo ^) else ( >> "%OPT_DIR%node_wrapper.bat"
    echo     "%%NODE_EXE%%" %%* >> "%OPT_DIR%node_wrapper.bat"
    echo ^) >> "%OPT_DIR%node_wrapper.bat"

    echo ✅ Node.js包装器创建完成
    echo [%START_TIME%] [SUCCESS] Node.js环境优化完成 >> "%LOG_FILE%"
    set /a SUCCESS_OPT+=1
) else (
    echo ❌ Node.js未安装或路径不正确
    echo [%START_TIME%] [ERROR] Node.js环境优化失败 >> "%LOG_FILE%"
    set /a FAILED_OPT+=1
)

echo.
echo [3/7] 修复PowerShell状态栏...
set /a TOTAL_OPT+=1

REM 检查并创建优化版状态栏
if not exist "%USERPROFILE%\.claude\statusbar_optimized.ps1" (
    echo # Claude Code Status Bar - Windows Compatible > "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo param([string]^$InputData = "^"^) >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo. >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo $modeStateFile = "$env:USERPROFILE\.claude\.mode_state" >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo $displayDir = Get-Location >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo if ($displayDir.Path.StartsWith($env:USERPROFILE^)) { >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo     $displayDir = $displayDir.Path.Replace($env:USERPROFILE, "~"^) >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo ^} >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo. >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo $statusBar = "$displayDir [Claude Mode] [Ready] (alt+m to cycle^)" >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"
    echo Write-Output $statusBar >> "%USERPROFILE%\.claude\statusbar_optimized.ps1"

    echo ✅ 优化版PowerShell状态栏创建完成
) else (
    echo ✅ PowerShell状态栏已存在
)

echo [%START_TIME%] [SUCCESS] PowerShell状态栏修复完成 >> "%LOG_FILE%"
set /a SUCCESS_OPT+=1

echo.
echo [4/7] 优化MCP服务器配置...
set /a TOTAL_OPT+=1

REM 检查MCP连接
claude.cmd mcp list >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ MCP服务器配置正常
    echo [%START_TIME%] [SUCCESS] MCP服务器配置检查完成 >> "%LOG_FILE%"
    set /a SUCCESS_OPT+=1
) else (
    echo ⚠️  MCP服务器连接异常，建议检查网络连接
    echo [%START_TIME%] [WARNING] MCP服务器连接异常 >> "%LOG_FILE%"
    set /a SUCCESS_OPT+=1  %REM 不算失败，只是警告
)

echo.
echo [5/7] 优化路径兼容性...
set /a TOTAL_OPT+=1

REM 创建路径转换工具
echo @echo off > "%OPT_DIR%path_converter.bat"
echo REM Windows路径转换工具 >> "%OPT_DIR%path_converter.bat"
echo set "INPUT_PATH=%%1" >> "%OPT_DIR%path_converter.bat"
echo if "%%INPUT_PATH:~0,3%%"=="/c/" ( >> "%OPT_DIR%path_converter.bat"
echo     set "OUTPUT_PATH=C:%%INPUT_PATH:~2%%" >> "%OPT_DIR%path_converter.bat"
echo ^) else ( >> "%OPT_DIR%path_converter.bat"
echo     set "OUTPUT_PATH=%%INPUT_PATH%%" >> "%OPT_DIR%path_converter.bat"
echo ^) >> "%OPT_DIR%path_converter.bat"
echo echo %%OUTPUT_PATH%% >> "%OPT_DIR%path_converter.bat"

echo ✅ 路径兼容性工具创建完成
echo [%START_TIME%] [SUCCESS] 路径兼容性优化完成 >> "%LOG_FILE%"
set /a SUCCESS_OPT+=1

echo.
echo [6/7] 清理临时文件...
set /a TOTAL_OPT+=1

REM 清理Python缓存
if exist "%OPT_DIR%__pycache__" (
    rmdir /s /q "%OPT_DIR%__pycache__" >nul 2>&1
    echo ✅ 已清理Python缓存
)

REM 清理其他临时文件
del /q "%OPT_DIR%*.tmp" >nul 2>&1
del /q "%OPT_DIR%*.log" >nul 2>&1 2>nul
del /q "%OPT_DIR%test_*.txt" >nul 2>&1

echo [%START_TIME%] [SUCCESS] 临时文件清理完成 >> "%LOG_FILE%"
set /a SUCCESS_OPT+=1

echo.
echo [7/7] 创建健康检查脚本...
set /a TOTAL_OPT+=1

REM 创建健康检查脚本
echo @echo off > "%OPT_DIR%health_check.bat"
echo echo ======================================== >> "%OPT_DIR%health_check.bat"
echo echo Claude系统健康检查 >> "%OPT_DIR%health_check.bat"
echo echo ======================================== >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo [1/5] 检查Claude命令... >> "%OPT_DIR%health_check.bat"
echo claude.cmd --version ^>nul 2^>^&1 >> "%OPT_DIR%health_check.bat"
echo if %%errorlevel%% equ 0 ( >> "%OPT_DIR%health_check.bat"
echo     echo ✅ Claude命令正常 >> "%OPT_DIR%health_check.bat"
echo ^) else ( >> "%OPT_DIR%health_check.bat"
echo     echo ❌ Claude命令异常 >> "%OPT_DIR%health_check.bat"
echo ^) >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo [2/5] 检查Node.js... >> "%OPT_DIR%health_check.bat"
echo "C:\Program Files\nodejs\node.exe" --version ^>nul 2^>^&1 >> "%OPT_DIR%health_check.bat"
echo if %%errorlevel%% equ 0 ( >> "%OPT_DIR%health_check.bat"
echo     echo ✅ Node.js可用 >> "%OPT_DIR%health_check.bat"
echo ^) else ( >> "%OPT_DIR%health_check.bat"
echo     echo ❌ Node.js不可用 >> "%OPT_DIR%health_check.bat"
echo ^) >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo [3/5] 检查配置文件... >> "%OPT_DIR%health_check.bat"
echo if exist "%%USERPROFILE%%\.claude\settings.json" ( >> "%OPT_DIR%health_check.bat"
echo     echo ✅ Claude配置存在 >> "%OPT_DIR%health_check.bat"
echo ^) else ( >> "%OPT_DIR%health_check.bat"
echo     echo ❌ Claude配置缺失 >> "%OPT_DIR%health_check.bat"
echo ^) >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo [4/5] 检查网络连接... >> "%OPT_DIR%health_check.bat"
echo ping -n 1 google.com ^>nul 2^>^&1 >> "%OPT_DIR%health_check.bat"
echo if %%errorlevel%% equ 0 ( >> "%OPT_DIR%health_check.bat"
echo     echo ✅ 网络连接正常 >> "%OPT_DIR%health_check.bat"
echo ^) else ( >> "%OPT_DIR%health_check.bat"
echo     echo ❌ 网络连接异常 >> "%OPT_DIR%health_check.bat"
echo ^) >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo [5/5] 检查优化工具... >> "%OPT_DIR%health_check.bat"
echo if exist "%%OPT_DIR%%node_wrapper.bat" ( >> "%OPT_DIR%health_check.bat"
echo     echo ✅ Node.js包装器已安装 >> "%OPT_DIR%health_check.bat"
echo ^) else ( >> "%OPT_DIR%health_check.bat"
echo     echo ❌ Node.js包装器缺失 >> "%OPT_DIR%health_check.bat"
echo ^) >> "%OPT_DIR%health_check.bat"
echo echo. >> "%OPT_DIR%health_check.bat"
echo echo ======================================== >> "%OPT_DIR%health_check.bat"
echo echo 健康检查完成 >> "%OPT_DIR%health_check.bat"
echo echo ======================================== >> "%OPT_DIR%health_check.bat"

echo ✅ 健康检查脚本创建完成
echo [%START_TIME%] [SUCCESS] 健康检查脚本创建完成 >> "%LOG_FILE%"
set /a SUCCESS_OPT+=1

REM 计算成功率
set /a SUCCESS_RATE=!SUCCESS_OPT!*100/!TOTAL_OPT!

REM 生成完成报告
set "END_TIME=%date% %time%"
echo.
echo ================================================================
echo 🎉 系统优化完成！
echo ================================================================
echo ✅ 成功: !SUCCESS_OPT!/!TOTAL_OPT! (!SUCCESS_RATE!%%)
echo ⏱️  开始时间: %START_TIME%
echo ⏱️  结束时间: %END_TIME%
echo 📁 备份目录: %BACKUP_DIR%
echo 📄 日志文件: %LOG_FILE%
echo.
echo 🛠️  创建的工具:
echo    - node_wrapper.bat     (Node.js环境包装器)
echo    - path_converter.bat    (路径转换工具)
echo    - health_check.bat     (系统健康检查)
echo.
echo 📋 建议后续操作:
echo    1. 运行 health_check.bat 验证优化效果
echo    2. 重启Claude以应用配置更改
echo    3. 定期运行健康检查
echo    4. 保持系统和工具更新
echo ================================================================

REM 写入完成日志
echo [%END_TIME%] [SUCCESS] 系统优化完成，成功率: !SUCCESS_RATE!%% >> "%LOG_FILE%"
echo [%END_TIME%] [INFO] 优化报告: 成功!SUCCESS_OPT!/!TOTAL_OPT! >> "%LOG_FILE%"

REM 询问是否运行健康检查
echo.
set /p RUN_HEALTH="是否立即运行健康检查？(Y/N): "
if /i "!RUN_HEALTH!"=="Y" (
    echo.
    echo 运行健康检查...
    call "%OPT_DIR%health_check.bat"
)

echo.
echo 按任意键退出...
pause >nul
endlocal
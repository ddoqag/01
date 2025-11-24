@echo off
REM 一键设置DeepSeek环境变量

echo 🚀 DeepSeek 环境变量自动配置
echo =====================================

REM 方法1: 尝试从DZH系统动态获取
echo 🔍 正在从DZH系统获取Token...

python -c "
import sys
import os
sys.path.append('D:/dzh365(64)')
try:
    from token_config import DZHTokenManager
    tm = DZHTokenManager()
    token = tm.get_token('production_api') or tm.get_token('demo_token')
    if token:
        print(f'✅ 找到Token: {token[:20]}...')
        os.system(f'setx DEEPSEEK_CURRENT_TOKEN {token}')
        print('✅ 环境变量设置成功!')
        print('请重新打开命令行窗口以使环境变量生效')
    else:
        print('❌ 未找到可用Token')
except Exception as e:
    print(f'❌ 获取失败: {e}')
    print('请手动设置环境变量')
"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 🔧 手动设置方法:
    echo.
    echo 1. 临时设置(当前窗口有效):
    echo    set DEEPSEEK_CURRENT_TOKEN=your_token_here
    echo.
    echo 2. 永久设置(系统级):
    echo    setx DEEPSEEK_CURRENT_TOKEN your_token_here
    echo.
    echo 3. 使用脚本自动配置:
    echo    dt auto
    echo.
    echo 4. 直接运行Token管理:
    echo    python deepseek_token_manager.py status
)

echo.
echo ✅ 配置完成后，可以使用以下方式测试:
echo   dt test
echo   ds ask "测试问题"
echo   或直接对话: 请用DeepSeek帮我分析一下

pause
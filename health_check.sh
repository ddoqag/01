#!/bin/bash
echo "========================================"
echo "Claude系统健康检查"
echo "========================================"
echo
echo "[1/5] 检查Claude命令..."
./claude.cmd --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Claude命令正常"
else
    echo "❌ Claude命令异常"
fi
echo
echo "[2/5] 检查Node.js..."
"/c/Program Files/nodejs/node.exe" --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Node.js可用"
else
    echo "❌ Node.js不可用"
fi
echo
echo "[3/5] 检查配置文件..."
if [ -f ~/.claude/settings.json ]; then
    echo "✅ Claude配置存在"
else
    echo "❌ Claude配置缺失"
fi
echo
echo "[4/5] 检查网络连接..."
ping -c 1 google.com >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 网络连接正常"
else
    echo "❌ 网络连接异常"
fi
echo
echo "[5/5] 检查优化工具..."
if [ -f ./node_wrapper.bat ]; then
    echo "✅ Node.js包装器已安装"
else
    echo "⚠️ Node.js包装器缺失"
fi
echo
echo "========================================"
echo "健康检查完成"
echo "========================================"

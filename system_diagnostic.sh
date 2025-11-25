#!/bin/bash
# 系统诊断工具

echo "=== 系统诊断报告 ==="
echo "生成时间: $(date)"
echo

echo "=== 基本信息 ==="
echo "操作系统: $(uname -a)"
echo "当前目录: $(pwd)"
echo "用户: $(whoami)"
echo

echo "=== Node.js环境 ==="
if command -v node >/dev/null 2>&1; then
    echo "Node.js版本: $(node --version)"
    echo "Node.js路径: $(which node)"
else
    echo "Node.js: 未找到"
fi

if command -v npm >/dev/null 2>&1; then
    echo "NPM版本: $(npm --version)"
    echo "NPM路径: $(which npm)"
else
    echo "NPM: 未找到"
fi
echo

echo "=== PowerShell环境 ==="
if command -v powershell >/dev/null 2>&1; then
    echo "PowerShell: 可用"
    powershell -Command '$PSVersionTable.PSVersion.ToString()' 2>/dev/null || echo "版本获取失败"
else
    echo "PowerShell: 未找到"
fi
echo

echo "=== 环境变量 ==="
echo "PATH (前10个):"
echo "$PATH" | tr ':' '\n' | head -10
echo

echo "=== 网络连接 ==="
if command -v ping >/dev/null 2>&1; then
    echo "测试网络连接..."
    ping -n 1 8.8.8.8 >/dev/null 2>&1 && echo "外网连接: 正常" || echo "外网连接: 异常"
fi
echo

echo "=== 诊断完成 ==="

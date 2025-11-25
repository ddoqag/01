#!/bin/bash
# 性能优化脚本

echo "=== 系统性能优化 ==="

# 优化Shell环境
echo "优化Shell环境..."
# 设置更快的文件系统访问
export MSYS2_PATH_TYPE=inherit
export MSYS_NO_PATHCONV=1

# 优化Node.js环境
echo "优化Node.js环境..."
export NODE_OPTIONS="--max-old-space-size=4096"
export npm_config_registry="https://registry.npmmirror.com/"

# 设置环境变量
echo "设置环境变量..."
export NODE_PATH="/c/Program Files/nodejs"
export NPM_PATH="/c/Program Files/nodejs"

echo "性能优化完成"
echo "请运行 'source performance_optimizer.sh' 使设置生效"

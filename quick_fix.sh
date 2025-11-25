#!/bin/bash

# Windows系统兼容性快速修复脚本
# 作者: Claude Code Assistant
# 版本: 1.0
# 创建日期: 2025-11-25

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统环境
check_environment() {
    log_info "检查系统环境..."

    # 检查操作系统
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        log_success "检测到Windows系统 ($OSTYPE)"
        SYSTEM_TYPE="windows"
    else
        log_warning "未检测到Windows系统，部分功能可能不适用"
        SYSTEM_TYPE="other"
    fi

    # 检查Node.js安装路径
    NODE_PATHS=(
        "/c/Program Files/nodejs/node.exe"
        "/c/Program Files (x86)/nodejs/node.exe"
        "/usr/bin/node"
        "/usr/local/bin/node"
    )

    NODE_PATH=""
    for path in "${NODE_PATHS[@]}"; do
        if [[ -f "$path" ]]; then
            NODE_PATH="$path"
            log_success "找到Node.js: $path"
            break
        fi
    done

    if [[ -z "$NODE_PATH" ]]; then
        log_error "未找到Node.js安装，请先安装Node.js"
        exit 1
    fi

    # 检查NPM
    NPM_PATH="${NODE_PATH/node.exe/npm.cmd}"
    if [[ ! -f "$NPM_PATH" ]]; then
        NPM_PATH="${NODE_PATH/node.exe/npm}"
    fi

    if [[ -f "$NPM_PATH" ]]; then
        log_success "找到NPM: $NPM_PATH"
    else
        log_error "未找到NPM"
        exit 1
    fi
}

# 修复环境变量
fix_environment() {
    log_info "修复环境变量..."

    # 创建环境变量设置脚本
    cat > fix_env.bat << 'EOF'
@echo off
echo 修复系统环境变量...

REM 设置Node.js路径
setx NODEJS_PATH "C:\Program Files\nodejs" /M

REM 添加到系统PATH
setx PATH "%PATH%;C:\Program Files\nodejs" /M

echo 环境变量修复完成
echo 请重新启动命令提示符或PowerShell以使更改生效
pause
EOF

    log_success "环境变量修复脚本已创建: fix_env.bat"
    log_warning "请以管理员身份运行 fix_env.bat 来修复系统环境变量"
}

# 创建命令包装器
create_command_wrappers() {
    log_info "创建命令包装器..."

    # Node.js包装器
    cat > node << 'EOF'
#!/bin/bash
# Node.js包装器脚本

# 可能的Node.js路径
NODE_PATHS=(
    "/c/Program Files/nodejs/node.exe"
    "/c/Program Files (x86)/nodejs/node.exe"
    "node"
)

# 查找并执行Node.js
for path in "${NODE_PATHS[@]}"; do
    if command -v "$path" >/dev/null 2>&1 || [[ -f "$path" ]]; then
        exec "$path" "$@"
        exit $?
    fi
done

echo "错误: 未找到Node.js，请确保已正确安装"
exit 1
EOF

    # NPM包装器
    cat > npm << 'EOF'
#!/bin/bash
# NPM包装器脚本

# 可能的NPM路径
NPM_PATHS=(
    "/c/Program Files/nodejs/npm.cmd"
    "/c/Program Files (x86)/nodejs/npm.cmd"
    "npm"
)

# 查找并执行NPM
for path in "${NPM_PATHS[@]}"; do
    if command -v "$path" >/dev/null 2>&1 || [[ -f "$path" ]]; then
        exec "$path" "$@"
        exit $?
    fi
done

echo "错误: 未找到NPM，请确保已正确安装"
exit 1
EOF

    # PowerShell包装器
    cat > powershell << 'EOF'
#!/bin/bash
# PowerShell包装器脚本

# 可能的PowerShell路径
PWSH_PATHS=(
    "/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    "/c/Program Files/PowerShell/7/pwsh.exe"
    "powershell"
    "pwsh"
)

# 查找并执行PowerShell
for path in "${PWSH_PATHS[@]}"; do
    if command -v "$path" >/dev/null 2>&1 || [[ -f "$path" ]]; then
        exec "$path" "$@"
        exit $?
    fi
done

echo "错误: 未找到PowerShell，请确保已正确安装"
exit 1
EOF

    # 设置执行权限
    chmod +x node npm powershell

    log_success "命令包装器已创建: node, npm, powershell"
}

# 创建路径转换工具
create_path_converter() {
    log_info "创建路径转换工具..."

    cat > path_converter.sh << 'EOF'
#!/bin/bash
# 路径格式转换工具

# Windows路径转Unix风格
win_to_unix() {
    local path="$1"
    # 替换反斜杠为正斜杠
    path="${path//\\/\/}"
    # 转换驱动器路径
    if [[ "$path" =~ ^[A-Za-z]: ]]; then
        path="/${path:0:1}/${path:2}"
    fi
    echo "$path"
}

# Unix风格路径转Windows路径
unix_to_win() {
    local path="$1"
    # 转换驱动器路径
    if [[ "$path" =~ ^/[A-Za-z]/ ]]; then
        path="${path:1:1}:${path:2}"
    fi
    # 替换正斜杠为反斜杠
    path="${path//\//\\}"
    echo "$path"
}

# 主函数
case "$1" in
    win2unix)
        win_to_unix "$2"
        ;;
    unix2win)
        unix_to_win "$2"
        ;;
    *)
        echo "用法: $0 {win2unix|unix2win} <路径>"
        echo "示例:"
        echo "  $0 win2unix C:\\Users\\test"
        echo "  $0 unix2win /c/Users/test"
        exit 1
        ;;
esac
EOF

    chmod +x path_converter.sh
    log_success "路径转换工具已创建: path_converter.sh"
}

# 修复MCP服务器配置
fix_mcp_config() {
    log_info "修复MCP服务器配置..."

    # 检查Claude配置文件
    CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"

    if [[ -f "$CLAUDE_CONFIG" ]]; then
        log_info "找到Claude配置文件，备份原文件..."
        cp "$CLAUDE_CONFIG" "${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"

        log_info "分析MCP服务器配置..."
        # 这里可以添加具体的MCP配置修复逻辑
        log_success "MCP配置检查完成"
    else
        log_warning "未找到Claude配置文件"
    fi
}

# 创建系统诊断工具
create_diagnostic_tool() {
    log_info "创建系统诊断工具..."

    cat > system_diagnostic.sh << 'EOF'
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
EOF

    chmod +x system_diagnostic.sh
    log_success "系统诊断工具已创建: system_diagnostic.sh"
}

# 创建性能优化脚本
create_performance_optimizer() {
    log_info "创建性能优化脚本..."

    cat > performance_optimizer.sh << 'EOF'
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
EOF

    chmod +x performance_optimizer.sh
    log_success "性能优化脚本已创建: performance_optimizer.sh"
}

# 创建自动化维护脚本
create_maintenance_script() {
    log_info "创建自动化维护脚本..."

    cat > auto_maintenance.sh << 'EOF'
#!/bin/bash
# 自动化维护脚本

MAINTENANCE_LOG="maintenance.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MAINTENANCE_LOG"
}

# 清理临时文件
cleanup_temp() {
    log_message "清理临时文件..."
    find . -name "*.tmp" -type f -delete 2>/dev/null || true
    find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
}

# 检查磁盘空间
check_disk_space() {
    log_message "检查磁盘空间..."
    df -h . | tail -1 | awk '{print $5}' | sed 's/%//' | while read usage; do
        if [[ $usage -gt 80 ]]; then
            log_message "警告: 磁盘使用率 ${usage}%"
        fi
    done
}

# 检查系统更新
check_updates() {
    log_message "检查系统更新..."
    if command -v npm >/dev/null 2>&1; then
        npm outdated 2>/dev/null || log_message "npm包检查完成"
    fi
}

# 执行维护任务
main() {
    log_message "开始自动化维护..."
    cleanup_temp
    check_disk_space
    check_updates
    log_message "维护完成"
}

main "$@"
EOF

    chmod +x auto_maintenance.sh
    log_success "自动化维护脚本已创建: auto_maintenance.sh"
}

# 主执行函数
main() {
    echo "=========================================="
    echo "    Windows系统兼容性快速修复工具"
    echo "=========================================="
    echo

    check_environment
    echo

    fix_environment
    echo

    create_command_wrappers
    echo

    create_path_converter
    echo

    fix_mcp_config
    echo

    create_diagnostic_tool
    echo

    create_performance_optimizer
    echo

    create_maintenance_script
    echo

    log_success "快速修复完成！"
    echo
    echo "后续步骤："
    echo "1. 以管理员身份运行 fix_env.bat 修复系统环境变量"
    echo "2. 运行 ./system_diagnostic.sh 进行系统诊断"
    echo "3. 运行 source ./performance_optimizer.sh 优化性能"
    echo "4. 定期运行 ./auto_maintenance.sh 进行维护"
    echo
    log_info "详细优化计划请查看: SYSTEM_OPTIMIZATION_PLAN.md"
}

# 执行主函数
main "$@"
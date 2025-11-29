#!/bin/bash
# Claude Code Wrapper for Git Bash/WSL environments
# 解决跨平台兼容性问题

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Claude Code CLI路径
CLAUDE_CLI="$SCRIPT_DIR/node_modules/@anthropic-ai/claude-code/cli.js"

# 检查Claude Code CLI是否存在
if [[ ! -f "$CLAUDE_CLI" ]]; then
    echo "Error: Claude Code CLI not found at $CLAUDE_CLI" >&2
    echo "Please ensure Claude Code is properly installed via npm" >&2
    exit 1
fi

# 查找Node.js
find_node() {
    # 1. 检查npm目录中的node
    if [[ -f "$SCRIPT_DIR/node.exe" ]]; then
        echo "$SCRIPT_DIR/node.exe"
        return 0
    fi

    # 2. 检查Windows系统PATH中的node
    if command -v node.exe >/dev/null 2>&1; then
        echo "node.exe"
        return 0
    fi

    # 3. 检查Linux/WSL PATH中的node
    if command -v node >/dev/null 2>&1; then
        echo "node"
        return 0
    fi

    # 4. 尝试常见安装路径
    local common_paths=(
        "/mnt/c/Program Files/nodejs/node.exe"
        "/mnt/c/Program Files (x86)/nodejs/node.exe"
        "$APPDATA/../Local/Programs/Microsoft VS Code/bin/code.cmd"
    )

    for path in "${common_paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    done

    return 1
}

# 查找并验证Node.js
NODE_CMD=$(find_node)
if [[ $? -ne 0 ]]; then
    echo "Error: Node.js not found. Please install Node.js first." >&2
    exit 1
fi

# 验证Node.js可以正常执行
if ! "$NODE_CMD" --version >/dev/null 2>&1; then
    echo "Error: Node.js at '$NODE_CMD' is not working properly" >&2
    exit 1
fi

# 设置环境变量
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://open.bigmodel.cn/api/anthropic}"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-1}"

# 启动Claude Code
if [[ "$1" == "--verbose" ]]; then
    echo "Claude Code Wrapper Debug Info:"
    echo "  Script directory: $SCRIPT_DIR"
    echo "  CLI path: $CLAUDE_CLI"
    echo "  Node.js command: $NODE_CMD"
    echo "  Arguments: ${@:2}"
    echo
fi

# 执行Claude Code CLI，传递所有参数
exec "$NODE_CMD" "$CLAUDE_CLI" "$@"

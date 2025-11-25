#!/bin/bash
# 路径格式转换工具

# Windows路径转Unix风格
win_to_unix() {
    local path="$1"
    # 替换反斜杠为正斜杠
    path="${path//\\/\/}"
    # 转换驱动器路径
    if [[ "$path" =~ ^[A-Za-z]: ]]; then
        path="/${path:0:1,1}/${path:3}"
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

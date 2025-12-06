#!/bin/bash
# Claude Code Status Bar Script
# 显示当前工作目录和快捷键信息

pwd=$(pwd)
home_dir="$HOME"

# 如果在用户目录下，显示相对路径
if [[ "$pwd" == "$home_dir"* ]]; then
    display_path="~${pwd#$home_dir}"
else
    display_path="$pwd"
fi

# 输出状态栏信息
echo "⏵⏵ accept edits on (shift+tab to cycle) $display_path cd"
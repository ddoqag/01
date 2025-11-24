#!/bin/bash
# AgentFlow底部状态显示脚本 - Windows兼容优化版本

# 检测操作系统
IS_WINDOWS=false
if [[ "$(uname -s)" == *MINGW* ]] || [[ "$(uname -s)" == *MSYS* ]] || [[ "$(uname -s)" == *CYGWIN* ]]; then
    IS_WINDOWS=true
fi

# ANSI颜色代码 - Windows兼容性优化
if [ "$IS_WINDOWS" = true ]; then
    # Windows环境下使用更兼容的颜色代码
    RED='\033[31m'
    GREEN='\033[32m'
    YELLOW='\033[33m'
    BLUE='\033[34m'
    PURPLE='\033[35m'
    CYAN='\033[36m'
    WHITE='\033[37m'
    GRAY='\033[90m'
    RESET='\033[0m'

    # 确保ANSI颜色在Windows终端中工作
    export COLORTERM=truecolor
else
    # Unix/Linux系统保持原有设置
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    WHITE='\033[1;37m'
    GRAY='\033[0;90m'
    RESET='\033[0m'
fi

# Windows兼容的图标备用方案 (如果emoji不能显示)
FALLBACK_FLOW_ICON="[F]"
FALLBACK_AGENTFLOW_ICON="[A]"
FALLBACK_FUSION_ICON="[X]"
FALLBACK_UNKNOWN_ICON="[?]"

# 获取终端宽度 (Windows兼容)
TERM_WIDTH=$(tput cols 2>/dev/null || echo 80)

# Windows兼容的系统信息获取
get_system_info() {
    # 获取用户名
    user=$(whoami 2>/dev/null || echo "User")

    # 获取主机名 (Windows兼容)
    if command -v hostname >/dev/null 2>&1; then
        if [ "$IS_WINDOWS" = true ]; then
            host=$(hostname 2>/dev/null || echo "PC")
        else
            host=$(hostname -s 2>/dev/null || hostname 2>/dev/null || echo "Host")
        fi
    else
        host="PC"
    fi

    # 获取当前目录
    current_dir=$(pwd)

    # 检测是否为工作目录
    if [[ "$current_dir" == *"claude"* ]] || [[ "$current_dir" == *"AgentFlow"* ]]; then
        current_dir="$current_dir 🚀"
    elif [[ "$current_dir" == "$HOME"* ]]; then
        # 简化home目录显示
        home_pattern="$HOME"
        current_dir=$(echo "$current_dir" | sed "s|$home_pattern|~|")
    fi

    # 获取当前时间
    current_time=$(date "+%H:%M:%S" 2>/dev/null || echo "00:00:00")

    # Windows兼容的负载获取
    if command -v uptime >/dev/null 2>&1; then
        load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' 2>/dev/null || echo "0.0")
    elif [ "$IS_WINDOWS" = true ]; then
        # Windows环境下使用CPU使用率模拟负载
        load_avg="0.1"  # 简化显示
    else
        load_avg="N/A"
    fi
}

# 获取AgentFlow模式状态
get_mode_info() {
    # 检测不同的模式文件位置
    local mode_locations=(
        "$HOME/.flow/.current_mode"
        "$HOME/flow/.current_mode"
        "./.flow/.current_mode"
        "./flow/.current_mode"
        "$HOME/.current_mode"
    )

    current_mode="flow"  # 默认模式

    for mode_file in "${mode_locations[@]}"; do
        if [ -f "$mode_file" ]; then
            current_mode=$(cat "$mode_file" 2>/dev/null || echo "flow")
            break
        fi
    done

    # 设置模式信息
    case "$current_mode" in
        "flow")
            mode_icon="🎯"
            mode_name="Flow"
            mode_color="${CYAN}"
            mode_indicator="[●FLOW•○AGENTFLOW•○FUSION]"
            mode_desc="专业Agent直接调用"
            fallback_icon="$FALLBACK_FLOW_ICON"
            ;;
        "agentflow")
            mode_icon="🔗"
            mode_name="AgentFlow"
            mode_color="${YELLOW}"
            mode_indicator="[○FLOW•●AGENTFLOW•○FUSION]"
            mode_desc="多Agent工作流协调"
            fallback_icon="$FALLBACK_AGENTFLOW_ICON"
            ;;
        "fusion")
            mode_icon="🚀"
            mode_name="Fusion"
            mode_color="${PURPLE}"
            mode_indicator="[○FLOW•○AGENTFLOW•●FUSION]"
            mode_desc="Flow+AgentFlow智能协作"
            fallback_icon="$FALLBACK_FUSION_ICON"
            ;;
        *)
            mode_icon="📋"
            mode_name="Unknown"
            mode_color="${WHITE}"
            mode_indicator="[???]"
            mode_desc="未知模式"
            fallback_icon="$FALLBACK_UNKNOWN_ICON"
            ;;
    esac
}

# 测试图标显示能力
test_icon_support() {
    # 简单测试：尝试显示emoji，如果失败则使用fallback
    echo -e "🎯" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "$mode_icon"
    else
        echo "$fallback_icon"
    fi
}

# 设置负载颜色
set_load_color() {
    if [[ "$load_avg" != "N/A" ]] && [[ "$load_avg" =~ ^[0-9] ]]; then
        load_num=${load_avg%.*}
        if [[ ${load_num} -gt 80 ]]; then
            load_color="${RED}"
        elif [[ ${load_num} -gt 50 ]]; then
            load_color="${YELLOW}"
        else
            load_color="${GREEN}"
        fi
    else
        load_color="${GRAY}"
    fi
}

# 创建状态栏函数
create_status_bar() {
    # Windows图标兼容性处理
    local display_icon
    if [ "$IS_WINDOWS" = true ]; then
        # Windows环境下优先使用fallback图标，确保显示
        display_icon="$fallback_icon"
    else
        display_icon="$mode_icon"
    fi

    local mode_status="${mode_color}${display_icon} ${mode_name}${RESET} ${GRAY}${mode_indicator}${RESET}"
    local system_status="${GRAY}${current_time}${RESET} ${load_color}${load_avg}${RESET} ${GRAY}83A${RESET}"
    local user_status="${GREEN}${user}@${host}${RESET}:${CYAN}${current_dir}${RESET}"

    # 修复长度计算
    local left_part="Alt+M: ${mode_status}"
    local middle_part="${user_status}"
    local right_part="${system_status} | CL-$(date +%H%M)"

    # 更安全的长度计算 - 过滤ANSI代码
    local left_len=$(echo -e "$left_part" | sed 's/\x1b\[[0-9;]*m//g' | wc -c | tr -d ' ')
    local middle_len=$(echo -e "$middle_part" | sed 's/\x1b\[[0-9;]*m//g' | wc -c | tr -d ' ')
    local right_len=$(echo -e "$right_part" | sed 's/\x1b\[[0-9;]*m//g' | wc -c | tr -d ' ')

    local total_text_len=$((left_len + middle_len + right_len + 6))  # +6 for separators
    local padding=$((TERM_WIDTH - total_text_len))

    if [ $padding -lt 0 ]; then
        padding=2
    fi

    local spaces=$(printf "%*s" $padding)

    echo -e "${left_part}${spaces}${middle_part} | ${right_part}"
}

# 显示底部状态栏
show_bottom_status() {
    echo ""
    echo -e "$(printf '─%.0s' $(seq 1 $TERM_WIDTH))"
    create_status_bar
    echo -e "$(printf '─%.0s' $(seq 1 $TERM_WIDTH))"
    echo ""
}

# 显示模式信息面板
show_mode_info() {
    echo ""
    local panel_width=70

    echo -e "${mode_color}╔$(printf '═%.0s' $(seq 1 $panel_width))╗${RESET}"
    echo -e "${mode_color}║${RESET} ${WHITE}${fallback_icon} ${mode_name} - ${mode_desc}${RESET} $(printf ' %.0s' $(seq 1 $((panel_width - ${#mode_name} - ${#mode_desc} - 8)))) ${mode_color}║${RESET}"
    echo -e "${mode_color}╠$(printf '═%.0s' $(seq 1 $panel_width))╣${RESET}"
    echo -e "${mode_color}║${RESET} ${GRAY}快捷键: Alt+M 切换模式 | Alt+S 显示状态 | /mode 命令切换${RESET} $(printf ' %.0s' $(seq 1 $((panel_width - 65)))) ${mode_color}║${RESET}"
    echo -e "${mode_color}╚$(printf '═%.0s' $(seq 1 $panel_width))╝${RESET}"
    echo ""
}

# 显示图标测试
show_icon_test() {
    echo ""
    echo -e "${CYAN}=== 图标显示测试 ===${RESET}"
    echo -e "Flow模式: ${fallback_icon} 🎯"
    echo -e "AgentFlow模式: ${FALLBACK_AGENTFLOW_ICON} 🔗"
    echo -e "Fusion模式: ${FALLBACK_FUSION_ICON} 🚀"
    echo -e "当前模式: ${mode_color}${fallback_icon} ${mode_name}${RESET}"
    echo ""
}

# 初始化函数
init() {
    get_system_info
    get_mode_info
    set_load_color

    # Windows环境下的额外设置
    if [ "$IS_WINDOWS" = true ]; then
        # 确保使用UTF-8编码
        export LANG=zh_CN.UTF-8
        export LC_ALL=zh_CN.UTF-8
    fi
}

# 主函数
main() {
    init

    case "${1:-minimal}" in
        "show"|"status")
            show_bottom_status
            ;;
        "info"|"mode")
            show_mode_info
            ;;
        "test")
            show_icon_test
            ;;
        "both")
            show_bottom_status
            show_mode_info
            ;;
        "minimal")
            # 紧凑模式：使用fallback图标确保显示
            echo -e " ${mode_color}${fallback_icon}${RESET}"
            ;;
        *)
            echo "用法: $0 {show|info|test|both|minimal}"
            echo "  show    - 显示底部状态栏"
            echo "  info    - 显示模式信息面板"
            echo "  test    - 测试图标显示"
            echo "  both    - 显示状态栏和信息面板"
            echo "  minimal - 紧凑模式（只显示图标）"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
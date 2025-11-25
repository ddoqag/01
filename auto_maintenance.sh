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

#!/bin/bash
# OpenClaw 定时备份脚本（cron 版本）
# 每天凌晨 2 点自动执行

set -e

# 配置
SCRIPT_DIR="/root/clawd"
BACKUP_SCRIPT="${SCRIPT_DIR}/scripts/auto_backup.py"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/cron_backup.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 创建日志目录
mkdir -p "$LOG_DIR"

# 开始备份
echo "==========================================" >> "$LOG_FILE"
echo "定时备份开始: $TIMESTAMP" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

# 检查备份脚本是否存在
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ 错误: 备份脚本不存在: $BACKUP_SCRIPT" >> "$LOG_FILE"
    exit 1
fi

# 执行备份
cd "$SCRIPT_DIR" || exit 1

if python3 "$BACKUP_SCRIPT" backup >> "$LOG_FILE" 2>&1; then
    echo "✅ 定时备份成功完成: $TIMESTAMP" >> "$LOG_FILE"
    exit 0
else
    echo "❌ 定时备份失败: $TIMESTAMP" >> "$LOG_FILE"
    exit 1
fi
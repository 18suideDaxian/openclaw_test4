#!/bin/bash
# OpenClaw 智能备份脚本
# 备份所有重要文件，支持增量备份和版本恢复

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="/root/clawd_backups"
CONFIG_DIR="/root/clawd"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="openclaw_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# 重要文件列表
IMPORTANT_FILES=(
    # 配置文件
    "AGENTS.md"
    "SOUL.md"
    "TOOLS.md"
    "IDENTITY.md"
    "USER.md"
    "MEMORY.md"
    "HEARTBEAT.md"
    "BOOTSTRAP.md"
    
    # 记忆文件
    "memory/"
    
    # 技能目录
    "skills/"
    
    # 配置目录
    "config/"
    
    # 脚本目录
    "scripts/"
    
    # OpenClaw 配置
    "/root/.openclaw/openclaw.json"
    "/root/.openclaw/extensions/"
    
    # QQBot 配置
    "/root/.openclaw/qqbot/"
)

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查目录
check_directories() {
    if [ ! -d "$CONFIG_DIR" ]; then
        print_error "OpenClaw 配置目录不存在: $CONFIG_DIR"
        exit 1
    fi
    
    mkdir -p "$BACKUP_DIR"
    print_success "备份目录: $BACKUP_DIR"
}

# 函数：创建备份
create_backup() {
    print_info "创建 OpenClaw 备份: $BACKUP_NAME"
    
    # 创建备份目录
    mkdir -p "$BACKUP_PATH"
    
    # 备份计数器
    backed_up=0
    skipped=0
    errors=0
    
    # 备份重要文件
    for item in "${IMPORTANT_FILES[@]}"; do
        source_path=""
        
        # 处理绝对路径和相对路径
        if [[ "$item" == /* ]]; then
            source_path="$item"
        else
            source_path="${CONFIG_DIR}/${item}"
        fi
        
        # 检查文件/目录是否存在
        if [ -e "$source_path" ]; then
            dest_path="${BACKUP_PATH}${source_path}"
            dest_dir=$(dirname "$dest_path")
            mkdir -p "$dest_dir"
            
            if cp -r "$source_path" "$dest_path" 2>/dev/null; then
                print_info "✅ 备份: $source_path"
                ((backed_up++))
            else
                print_warning "⚠️  跳过: $source_path (权限问题)"
                ((skipped++))
            fi
        else
            print_warning "⚠️  不存在: $source_path"
            ((skipped++))
        fi
    done
    
    # 创建备份清单
    create_backup_manifest
    
    # 压缩备份
    compress_backup
    
    print_success "备份完成!"
    print_info "备份统计:"
    print_info "  ✅ 成功备份: $backed_up 个文件/目录"
    print_info "  ⚠️  跳过: $skipped 个"
    print_info "  ❌ 错误: $errors 个"
    print_info "  📦 备份文件: ${BACKUP_PATH}.tar.gz"
    
    # 清理旧备份
    cleanup_old_backups
}

# 函数：创建备份清单
create_backup_manifest() {
    local manifest_file="${BACKUP_PATH}/BACKUP_MANIFEST.md"
    
    cat > "$manifest_file" << EOF
# OpenClaw 备份清单

## 备份信息
- **备份名称**: $BACKUP_NAME
- **备份时间**: $(date)
- **备份目录**: $BACKUP_PATH
- **源目录**: $CONFIG_DIR

## 包含的文件/目录

EOF
    
    # 列出所有备份的文件
    find "$BACKUP_PATH" -type f | while read -r file; do
        relative_path="${file#$BACKUP_PATH}"
        size=$(du -h "$file" | cut -f1)
        echo "- \`$relative_path\` ($size)" >> "$manifest_file"
    done
    
    # 添加统计信息
    total_files=$(find "$BACKUP_PATH" -type f | wc -l)
    total_size=$(du -sh "$BACKUP_PATH" | cut -f1)
    
    cat >> "$manifest_file" << EOF

## 统计信息
- **总文件数**: $total_files
- **总大小**: $total_size
- **备份类型**: 完整备份

## 恢复说明
要恢复此备份，请运行:
\`\`\`bash
cd /root/clawd
tar -xzf $BACKUP_DIR/${BACKUP_NAME}.tar.gz --strip-components=1
\`\`\`

或使用恢复脚本:
\`\`\`bash
./scripts/restore_openclaw.sh $BACKUP_NAME
\`\`\`

## 重要提示
1. 恢复前请备份当前配置
2. 恢复后可能需要重启 OpenClaw
3. 检查权限和文件所有权
4. 验证恢复的文件完整性

---
*备份时间: $(date)*
EOF
    
    print_success "已创建备份清单: $manifest_file"
}

# 函数：压缩备份
compress_backup() {
    print_info "压缩备份文件..."
    
    cd "$BACKUP_DIR" || exit 1
    
    if tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null; then
        compressed_size=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
        print_success "压缩完成: ${BACKUP_NAME}.tar.gz ($compressed_size)"
        
        # 删除未压缩的目录
        rm -rf "$BACKUP_NAME"
    else
        print_error "压缩失败"
        exit 1
    fi
}

# 函数：清理旧备份
cleanup_old_backups() {
    local keep_days=7
    local max_backups=10
    
    print_info "清理旧备份 (保留最近 $max_backups 个或 $keep_days 天内的备份)..."
    
    # 按时间排序，保留最新的
    cd "$BACKUP_DIR" || exit 1
    
    # 方法1: 保留最近 N 个备份
    backup_files=$(ls -t openclaw_backup_*.tar.gz 2>/dev/null || true)
    count=0
    
    for backup in $backup_files; do
        ((count++))
        if [ $count -gt $max_backups ]; then
            # 检查是否超过保留天数
            backup_date=$(echo "$backup" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
            if [ -n "$backup_date" ]; then
                backup_timestamp=$(date -d "${backup_date:0:8} ${backup_date:9:2}:${backup_date:11:2}:${backup_date:13:2}" +%s 2>/dev/null || echo 0)
                current_timestamp=$(date +%s)
                age_days=$(( (current_timestamp - backup_timestamp) / 86400 ))
                
                if [ $age_days -gt $keep_days ]; then
                    print_info "🗑️  删除旧备份: $backup (${age_days} 天前)"
                    rm -f "$backup"
                fi
            fi
        fi
    done
    
    print_success "备份清理完成"
}

# 函数：列出所有备份
list_backups() {
    print_info "可用备份列表:"
    echo "=" * 60
    
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR" || exit 1
        
        local count=0
        for backup in $(ls -t openclaw_backup_*.tar.gz 2>/dev/null || true); do
            ((count++))
            
            # 提取备份信息
            backup_date=$(echo "$backup" | grep -o '[0-9]\{8\}_[0-9]\{6\}' || echo "未知")
            size=$(du -h "$backup" | cut -f1)
            
            if [ "$backup_date" != "未知" ]; then
                # 格式化日期
                formatted_date="${backup_date:0:4}-${backup_date:4:2}-${backup_date:6:2} ${backup_date:9:2}:${backup_date:11:2}"
                echo "📦 $count. $backup"
                echo "   📅 时间: $formatted_date"
                echo "   📊 大小: $size"
                echo ""
            fi
        done
        
        if [ $count -eq 0 ]; then
            print_warning "暂无备份文件"
        else
            echo "=" * 60
            print_info "总计: $count 个备份"
        fi
    else
        print_warning "备份目录不存在: $BACKUP_DIR"
    fi
}

# 函数：显示帮助
show_help() {
    echo "OpenClaw 备份脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  backup    创建新备份 (默认)"
    echo "  list      列出所有备份"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 backup      # 创建新备份"
    echo "  $0 list        # 列出所有备份"
    echo "  $0             # 创建新备份"
    echo ""
    echo "备份位置: $BACKUP_DIR"
    echo "备份内容:"
    echo "  • 所有 skills"
    echo "  • 记忆文件 (memory/)"
    echo "  • 配置文件"
    echo "  • 脚本文件"
    echo "  • OpenClaw 系统配置"
    echo ""
    echo "💡 提示: 备份会自动压缩并清理旧备份"
}

# 主函数
main() {
    local command="${1:-backup}"
    
    echo "=========================================="
    echo "  OpenClaw 备份系统"
    echo "=========================================="
    echo ""
    
    case "$command" in
        "backup")
            check_directories
            create_backup
            ;;
        "list")
            list_backups
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    echo "=========================================="
    echo "  操作完成"
    echo "=========================================="
}

# 运行主函数
main "$@"
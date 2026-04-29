#!/bin/bash
# OpenClaw 恢复脚本
# 从备份中恢复文件，支持选择性恢复

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

# 函数：检查备份文件
check_backup_file() {
    local backup_name="$1"
    local backup_file="${BACKUP_DIR}/${backup_name}.tar.gz"
    
    if [ ! -f "$backup_file" ]; then
        # 尝试查找匹配的备份
        local matched_backups=$(ls "${BACKUP_DIR}/"*"${backup_name}"*".tar.gz" 2>/dev/null || true)
        
        if [ -z "$matched_backups" ]; then
            print_error "备份文件不存在: $backup_name"
            return 1
        elif [ $(echo "$matched_backups" | wc -l) -eq 1 ]; then
            # 只有一个匹配项
            backup_file="$matched_backups"
            backup_name=$(basename "$backup_file" .tar.gz)
            print_info "找到匹配的备份: $backup_name"
        else
            # 多个匹配项
            print_error "找到多个匹配的备份:"
            echo "$matched_backups" | while read -r bf; do
                echo "  • $(basename "$bf")"
            done
            return 1
        fi
    fi
    
    echo "$backup_file"
    return 0
}

# 函数：列出备份内容
list_backup_contents() {
    local backup_file="$1"
    
    print_info "备份内容预览:"
    echo "=" * 60
    
    # 列出压缩包中的文件
    if tar -tzf "$backup_file" 2>/dev/null | head -20; then
        total_files=$(tar -tzf "$backup_file" 2>/dev/null | wc -l)
        echo "..."
        print_info "总计: $total_files 个文件"
    else
        print_error "无法读取备份文件"
        return 1
    fi
    
    echo "=" * 60
}

# 函数：创建恢复前备份
create_pre_restore_backup() {
    print_info "创建恢复前备份..."
    
    local pre_restore_backup="${BACKUP_DIR}/pre_restore_$(date +"%Y%m%d_%H%M%S")"
    mkdir -p "$pre_restore_backup"
    
    # 备份当前的重要文件
    important_items=(
        "AGENTS.md"
        "SOUL.md"
        "TOOLS.md"
        "IDENTITY.md"
        "USER.md"
        "MEMORY.md"
        "memory/"
        "skills/"
        "config/"
    )
    
    for item in "${important_items[@]}"; do
        source_path="${CONFIG_DIR}/${item}"
        if [ -e "$source_path" ]; then
            cp -r "$source_path" "$pre_restore_backup/" 2>/dev/null || true
        fi
    done
    
    print_success "恢复前备份已创建: $pre_restore_backup"
}

# 函数：完全恢复
restore_full() {
    local backup_file="$1"
    
    print_warning "⚠️  警告: 这将覆盖当前所有文件!"
    read -p "是否继续? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "恢复已取消"
        return 1
    fi
    
    # 创建恢复前备份
    create_pre_restore_backup
    
    print_info "开始完全恢复..."
    
    # 解压到临时目录
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # 获取备份的根目录
    local backup_root=$(find "$temp_dir" -maxdepth 1 -type d -name "openclaw_backup_*" | head -1)
    
    if [ -z "$backup_root" ]; then
        print_error "无法找到备份根目录"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # 恢复文件
    print_info "恢复文件中..."
    
    # 恢复 skills
    if [ -d "${backup_root}/skills" ]; then
        print_info "恢复 skills..."
        rm -rf "${CONFIG_DIR}/skills"
        cp -r "${backup_root}/skills" "${CONFIG_DIR}/"
    fi
    
    # 恢复 memory
    if [ -d "${backup_root}/memory" ]; then
        print_info "恢复 memory..."
        rm -rf "${CONFIG_DIR}/memory"
        cp -r "${backup_root}/memory" "${CONFIG_DIR}/"
    fi
    
    # 恢复配置文件
    for config_file in "AGENTS.md" "SOUL.md" "TOOLS.md" "IDENTITY.md" "USER.md" "MEMORY.md"; do
        if [ -f "${backup_root}/${config_file}" ]; then
            print_info "恢复 ${config_file}..."
            cp "${backup_root}/${config_file}" "${CONFIG_DIR}/"
        fi
    done
    
    # 恢复 config 目录
    if [ -d "${backup_root}/config" ]; then
        print_info "恢复 config..."
        rm -rf "${CONFIG_DIR}/config"
        cp -r "${backup_root}/config" "${CONFIG_DIR}/"
    fi
    
    # 恢复 scripts 目录
    if [ -d "${backup_root}/scripts" ]; then
        print_info "恢复 scripts..."
        rm -rf "${CONFIG_DIR}/scripts"
        cp -r "${backup_root}/scripts" "${CONFIG_DIR}/"
    fi
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    print_success "完全恢复完成!"
}

# 函数：选择性恢复
restore_selective() {
    local backup_file="$1"
    
    print_info "选择性恢复模式"
    echo "=" * 60
    
    # 解压到临时目录
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # 获取备份的根目录
    local backup_root=$(find "$temp_dir" -maxdepth 1 -type d -name "openclaw_backup_*" | head -1)
    
    if [ -z "$backup_root" ]; then
        print_error "无法找到备份根目录"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # 显示可恢复的项目
    local restore_options=(
        "skills - 所有技能"
        "memory - 记忆文件"
        "config - 配置文件"
        "scripts - 脚本文件"
        "AGENTS.md - 代理配置"
        "SOUL.md - 灵魂文件"
        "TOOLS.md - 工具文件"
        "IDENTITY.md - 身份文件"
        "USER.md - 用户文件"
        "MEMORY.md - 记忆导航"
    )
    
    echo "请选择要恢复的项目 (输入编号，多个用逗号分隔，或输入 'all'):"
    echo ""
    
    for i in "${!restore_options[@]}"; do
        echo "  $((i+1)). ${restore_options[$i]}"
    done
    
    echo ""
    read -p "选择: " choices
    
    # 处理选择
    if [ "$choices" = "all" ]; then
        restore_full "$backup_file"
        rm -rf "$temp_dir"
        return 0
    fi
    
    # 创建恢复前备份
    create_pre_restore_backup
    
    # 恢复选中的项目
    IFS=',' read -ra selected <<< "$choices"
    
    for choice in "${selected[@]}"; do
        choice=$(echo "$choice" | tr -d ' ')
        index=$((choice-1))
        
        if [ $index -ge 0 ] && [ $index -lt ${#restore_options[@]} ]; then
            item_name=$(echo "${restore_options[$index]}" | cut -d' ' -f1)
            
            case "$item_name" in
                "skills")
                    print_info "恢复 skills..."
                    rm -rf "${CONFIG_DIR}/skills"
                    cp -r "${backup_root}/skills" "${CONFIG_DIR}/"
                    ;;
                "memory")
                    print_info "恢复 memory..."
                    rm -rf "${CONFIG_DIR}/memory"
                    cp -r "${backup_root}/memory" "${CONFIG_DIR}/"
                    ;;
                "config")
                    print_info "恢复 config..."
                    rm -rf "${CONFIG_DIR}/config"
                    cp -r "${backup_root}/config" "${CONFIG_DIR}/"
                    ;;
                "scripts")
                    print_info "恢复 scripts..."
                    rm -rf "${CONFIG_DIR}/scripts"
                    cp -r "${backup_root}/scripts" "${CONFIG_DIR}/"
                    ;;
                *)
                    # 恢复单个文件
                    if [ -f "${backup_root}/${item_name}" ]; then
                        print_info "恢复 ${item_name}..."
                        cp "${backup_root}/${item_name}" "${CONFIG_DIR}/"
                    else
                        print_warning "文件不存在: ${item_name}"
                    fi
                    ;;
            esac
        else
            print_warning "无效的选择: $choice"
        fi
    done
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    print_success "选择性恢复完成!"
}

# 函数：验证恢复
verify_restore() {
    print_info "验证恢复结果..."
    
    local verified=0
    local failed=0
    
    # 检查重要文件
    important_files=(
        "AGENTS.md"
        "SOUL.md"
        "skills/"
        "memory/"
    )
    
    for item in "${important_files[@]}"; do
        if [ -e "${CONFIG_DIR}/${item}" ]; then
            print_info "✅ ${item} 存在"
            ((verified++))
        else
            print_warning "⚠️  ${item} 不存在"
            ((failed++))
        fi
    done
    
    # 检查 skills 数量
    if [ -d "${CONFIG_DIR}/skills" ]; then
        skill_count=$(ls -la "${CONFIG_DIR}/skills/" | grep -c '^d' || echo 0)
        print_info "📦 Skills 数量: $skill_count"
    fi
    
    # 检查 memory 文件
    if [ -d "${CONFIG_DIR}/memory" ]; then
        memory_files=$(find "${CONFIG_DIR}/memory" -name "*.md" | wc -l)
        print_info "🧠 Memory 文件: $memory_files"
    fi
    
    echo ""
    print_info "验证结果:"
    print_info "  ✅ 验证通过: $verified"
    print_info "  ⚠️  验证失败: $failed"
    
    if [ $failed -eq 0 ]; then
        print_success "恢复验证通过!"
    else
        print_warning "恢复验证未完全通过，请检查"
    fi
}

# 函数：显示帮助
show_help() {
    echo "OpenClaw 恢复脚本"
    echo ""
    echo "用法: $0 <备份名称> [选项]"
    echo ""
    echo "选项:"
    echo "  --full        完全恢复 (覆盖所有文件)"
    echo "  --selective   选择性恢复 (默认)"
    echo "  --list        列出备份内容"
    echo "  --verify      验证恢复结果"
    echo "  --help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 openclaw_backup_20260413_090000          # 选择性恢复"
    echo "  $0 openclaw_backup_20260413_090000 --full   # 完全恢复"
    echo "  $0 openclaw_backup_20260413_090000 --list   # 列出内容"
    echo "  $0 --verify                                 # 验证恢复"
    echo ""
    echo "💡 提示:"
    echo "  • 恢复前会自动创建备份"
    echo "  • 可以使用部分备份名称进行匹配"
    echo "  • 恢复后建议重启 OpenClaw"
    echo ""
    echo "可用备份:"
    if [ -d "$BACKUP_DIR" ]; then
        ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 | while read -r backup; do
            echo "  • $(basename "$backup")"
        done
    else
        echo "  暂无备份"
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "  OpenClaw 恢复系统"
    echo "=========================================="
    echo ""
    
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    local backup_name=""
    local mode="selective"
    local do_list=false
    local do_verify=false
    
    # 解析参数
    while [ $# -gt 0 ]; do
        case "$1" in
            --full)
                mode="full"
                shift
                ;;
            --selective)
                mode="selective"
                shift
                ;;
            --list)
                do_list=true
                shift
                ;;
            --verify)
                do_verify=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                if [ -z "$backup_name" ]; then
                    backup_name="$1"
                else
                    print_error "未知参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 验证模式
    if [ "$do_verify" = true ]; then
        verify_restore
        exit 0
    fi
    
    if [ -z "$backup_name" ]; then
        print_error "请指定备份名称"
        show_help
        exit 1
    fi
    
    # 检查备份文件
    backup_file=$(check_backup_file "$backup_name")
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    print_info "使用备份: $(basename "$backup_file")"
    
    # 列出备份内容
    if [ "$do_list" = true ]; then
        list_backup_contents "$backup_file"
        exit 0
    fi
    
    # 执行恢复
    case "$mode" in
        "full")
            restore_full "$backup_file"
            ;;
        "selective")
            restore_selective "$backup_file"
            ;;
        *)
            print_error "未知恢复模式: $mode"
            exit 1
            ;;
    esac
    
    # 验证恢复
    verify_restore
    
    echo ""
    print_success "恢复完成!"
    print_info "建议: 重启 OpenClaw 以使更改生效"
    echo ""
    echo "=========================================="
    echo "  恢复操作完成"
    echo "=========================================="
}

# 运行主函数
main "$@"
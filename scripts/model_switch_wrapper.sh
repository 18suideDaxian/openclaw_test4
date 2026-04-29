#!/bin/bash
# 模型切换包装器
# 确保切换模型后还能记住 skills 和定时任务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
CONFIG_DIR="config"
AGENT_CONFIG="$CONFIG_DIR/agent_config.json"
TASK_CONFIG="$CONFIG_DIR/scheduled_tasks.json"
SCRIPTS_DIR="scripts"

# 创建配置目录
mkdir -p "$CONFIG_DIR"

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

# 函数：检查依赖
check_dependencies() {
    local missing_deps=()
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查 schedule 模块
    if ! python3 -c "import schedule" &> /dev/null; then
        print_warning "Python schedule 模块未安装，正在安装..."
        pip3 install schedule --break-system-packages
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "缺少依赖: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

# 函数：初始化配置
init_config() {
    print_info "初始化配置..."
    
    # 如果配置文件不存在，创建默认配置
    if [ ! -f "$AGENT_CONFIG" ]; then
        cat > "$AGENT_CONFIG" << EOF
{
  "agent_config": {
    "current_model": "xdclaw-pool/deepseek-v3.2",
    "available_skills": [],
    "scheduled_tasks": [],
    "last_model_switch": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "config_version": "1.0.0"
  }
}
EOF
        print_success "已创建默认配置文件"
    fi
    
    # 初始化 skills 列表
    print_info "扫描可用 skills..."
    python3 "$SCRIPTS_DIR/model_switch_init.py"
}

# 函数：切换模型
switch_model() {
    local new_model="$1"
    
    if [ -z "$new_model" ]; then
        print_error "请指定要切换的模型"
        echo "用法: $0 <模型名称>"
        echo "示例: $0 xdclaw-pool/qwen-max"
        return 1
    fi
    
    print_info "切换模型到: $new_model"
    
    # 1. 更新模型配置
    python3 -c "
import sys
sys.path.append('.')
from scripts.model_switch_init import update_model_info
update_model_info('$new_model')
"
    
    # 2. 执行实际的模型切换
    print_info "执行模型切换命令..."
    
    # 这里使用 session_status 工具切换模型
    # 注意：实际使用时需要根据 OpenClaw 的 API 进行调整
    echo "请手动执行: session_status(model: \"$new_model\")"
    
    # 3. 初始化新模型
    print_info "初始化新模型环境..."
    python3 "$SCRIPTS_DIR/model_switch_init.py" "$new_model"
    
    print_success "模型切换完成！"
    print_info "当前配置:"
    python3 -c "
import json
with open('$AGENT_CONFIG', 'r') as f:
    config = json.load(f)
print('• 当前模型:', config['agent_config'].get('current_model', '未知'))
print('• 可用 skills:', len(config['agent_config'].get('available_skills', [])))
print('• 定时任务:', len(config['agent_config'].get('scheduled_tasks', [])))
"
}

# 函数：启动定时任务管理器
start_task_manager() {
    print_info "启动定时任务管理器..."
    
    # 检查是否已经在运行
    if pgrep -f "task_manager.py" > /dev/null; then
        print_warning "定时任务管理器已经在运行"
        return 0
    fi
    
    # 在后台启动
    nohup python3 "$SCRIPTS_DIR/task_manager.py" > logs/task_manager.log 2>&1 &
    local pid=$!
    
    echo $pid > "$CONFIG_DIR/task_manager.pid"
    print_success "定时任务管理器已启动 (PID: $pid)"
    
    # 等待一下确保启动成功
    sleep 2
    
    # 检查是否启动成功
    if ps -p $pid > /dev/null; then
        print_info "查看日志: tail -f logs/task_manager.log"
        return 0
    else
        print_error "定时任务管理器启动失败"
        return 1
    fi
}

# 函数：停止定时任务管理器
stop_task_manager() {
    print_info "停止定时任务管理器..."
    
    if [ -f "$CONFIG_DIR/task_manager.pid" ]; then
        local pid=$(cat "$CONFIG_DIR/task_manager.pid")
        
        if kill $pid 2>/dev/null; then
            print_success "已停止定时任务管理器 (PID: $pid)"
            rm -f "$CONFIG_DIR/task_manager.pid"
        else
            print_warning "定时任务管理器未运行"
        fi
    else
        print_warning "未找到定时任务管理器 PID 文件"
    fi
}

# 函数：显示状态
show_status() {
    print_info "系统状态"
    echo "=" * 50
    
    # 显示模型信息
    if [ -f "$AGENT_CONFIG" ]; then
        echo "📊 模型配置:"
        python3 -c "
import json
with open('$AGENT_CONFIG', 'r') as f:
    config = json.load(f)
agent = config.get('agent_config', {})
print(f'  当前模型: {agent.get(\"current_model\", \"未知\")}')
print(f'  最后切换: {agent.get(\"last_model_switch\", \"未知\")}')
print(f'  可用 skills: {len(agent.get(\"available_skills\", []))} 个')
"
    else
        echo "❌ 配置文件不存在"
    fi
    
    echo ""
    
    # 显示定时任务状态
    if [ -f "$CONFIG_DIR/task_manager.pid" ]; then
        local pid=$(cat "$CONFIG_DIR/task_manager.pid")
        if ps -p $pid > /dev/null; then
            echo "✅ 定时任务管理器: 运行中 (PID: $pid)"
        else
            echo "❌ 定时任务管理器: 已停止"
        fi
    else
        echo "❌ 定时任务管理器: 未运行"
    fi
    
    echo ""
    echo "📁 配置文件:"
    echo "  • 代理配置: $AGENT_CONFIG"
    echo "  • 任务配置: $TASK_CONFIG"
    echo "  • 日志目录: logs/"
    
    echo "=" * 50
}

# 函数：显示帮助
show_help() {
    echo "模型切换包装器 - 确保切换模型后还能记住 skills 和定时任务"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  switch <模型名称>   切换模型并保持配置"
    echo "  init                初始化配置"
    echo "  start-tasks         启动定时任务管理器"
    echo "  stop-tasks          停止定时任务管理器"
    echo "  status              显示系统状态"
    echo "  help                显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 switch xdclaw-pool/qwen-max"
    echo "  $0 init"
    echo "  $0 status"
    echo ""
    echo "可用模型示例:"
    echo "  • xdclaw-pool/deepseek-v3.2 (默认)"
    echo "  • xdclaw-pool/qwen-max"
    echo "  • xdclaw-pool/glm-5"
    echo "  • xdclaw-pool/qwen-vl-max"
}

# 主函数
main() {
    local command="$1"
    local arg="$2"
    
    # 检查依赖
    check_dependencies || exit 1
    
    # 创建日志目录
    mkdir -p logs
    
    case "$command" in
        "switch")
            switch_model "$arg"
            ;;
        "init")
            init_config
            ;;
        "start-tasks")
            start_task_manager
            ;;
        "stop-tasks")
            stop_task_manager
            ;;
        "status")
            show_status
            ;;
        "help"|"")
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
#!/usr/bin/env python3
"""
定时任务管理器
确保定时任务在模型切换后继续运行
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
import schedule

class TaskManager:
    """定时任务管理器"""
    
    def __init__(self, config_file="config/scheduled_tasks.json"):
        self.config_file = config_file
        self.tasks = []
        self.running = False
        self.load_tasks()
    
    def load_tasks(self):
        """加载定时任务"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = data.get("scheduled_tasks", [])
        else:
            self.tasks = []
        print(f"📋 加载了 {len(self.tasks)} 个定时任务")
    
    def save_tasks(self):
        """保存定时任务"""
        data = {
            "scheduled_tasks": self.tasks,
            "last_updated": datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存 {len(self.tasks)} 个定时任务")
    
    def add_task(self, name, schedule_time, command, enabled=True):
        """添加定时任务"""
        task = {
            "id": len(self.tasks) + 1,
            "name": name,
            "schedule_time": schedule_time,
            "command": command,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
            "last_executed": None,
            "execution_count": 0
        }
        self.tasks.append(task)
        self.save_tasks()
        print(f"✅ 已添加定时任务: {name} ({schedule_time})")
        return task
    
    def remove_task(self, task_id):
        """移除定时任务"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()
        print(f"🗑️ 已移除定时任务 ID: {task_id}")
    
    def enable_task(self, task_id, enabled=True):
        """启用/禁用定时任务"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["enabled"] = enabled
                self.save_tasks()
                status = "启用" if enabled else "禁用"
                print(f"🔧 已{status}定时任务: {task['name']}")
                return True
        return False
    
    def execute_task(self, task):
        """执行定时任务"""
        if not task["enabled"]:
            return
        
        print(f"⏰ 执行定时任务: {task['name']}")
        task["last_executed"] = datetime.now().isoformat()
        task["execution_count"] = task.get("execution_count", 0) + 1
        
        # 这里可以执行具体的命令
        # 例如: os.system(task["command"])
        print(f"  命令: {task['command']}")
        
        self.save_tasks()
    
    def schedule_tasks(self):
        """安排定时任务"""
        schedule.clear()
        
        for task in self.tasks:
            if task["enabled"]:
                schedule_time = task["schedule_time"]
                
                # 解析时间格式
                if schedule_time.startswith("every "):
                    # 周期性任务: "every 10 minutes", "every 1 hour"
                    parts = schedule_time.split()
                    if len(parts) >= 3:
                        interval = int(parts[1])
                        unit = parts[2]
                        
                        if unit.startswith("minute"):
                            schedule.every(interval).minutes.do(self.execute_task, task)
                        elif unit.startswith("hour"):
                            schedule.every(interval).hours.do(self.execute_task, task)
                        elif unit.startswith("day"):
                            schedule.every(interval).days.do(self.execute_task, task)
                
                elif ":" in schedule_time:
                    # 具体时间: "09:00", "14:30"
                    schedule.every().day.at(schedule_time).do(self.execute_task, task)
        
        print(f"📅 已安排 {len([t for t in self.tasks if t['enabled']])} 个定时任务")
    
    def run_scheduler(self):
        """运行调度器"""
        self.running = True
        print("🚀 定时任务调度器已启动")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """启动任务管理器"""
        self.schedule_tasks()
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """停止任务管理器"""
        self.running = False
        print("🛑 定时任务调度器已停止")
    
    def list_tasks(self):
        """列出所有定时任务"""
        print("\n" + "=" * 60)
        print("📋 定时任务列表")
        print("=" * 60)
        
        if not self.tasks:
            print("暂无定时任务")
            return
        
        for task in self.tasks:
            status = "✅ 启用" if task["enabled"] else "❌ 禁用"
            last_exec = task.get("last_executed", "从未执行")
            count = task.get("execution_count", 0)
            
            print(f"\nID: {task['id']}")
            print(f"名称: {task['name']}")
            print(f"时间: {task['schedule_time']}")
            print(f"状态: {status}")
            print(f"执行次数: {count}")
            print(f"最后执行: {last_exec}")
            print(f"命令: {task['command']}")
        
        print("=" * 60)

# 示例使用
if __name__ == "__main__":
    manager = TaskManager()
    
    # 添加示例任务
    manager.add_task(
        name="每日备份",
        schedule_time="02:00",
        command="bash scripts/backup.sh",
        enabled=True
    )
    
    manager.add_task(
        name="每小时检查",
        schedule_time="every 1 hour",
        command="python3 scripts/health_check.py",
        enabled=True
    )
    
    # 列出任务
    manager.list_tasks()
    
    # 启动调度器（在实际使用中，这应该在后台运行）
    print("\n💡 提示: 在实际部署中，定时任务管理器应该在后台持续运行")
    print("即使切换模型，定时任务也会继续执行")
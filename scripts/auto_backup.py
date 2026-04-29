#!/usr/bin/env python3
"""
OpenClaw 自动备份脚本
每天自动备份重要文件，支持通知和清理
"""

import os
import json
import sys
import time
import shutil
import tarfile
from datetime import datetime, timedelta
import subprocess

class AutoBackup:
    """自动备份管理器"""
    
    def __init__(self, config_file="config/backup_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.backup_dir = self.config["backup_config"]["backup_dir"]
        self.ensure_directories()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "backup_config": {
                    "enabled": True,
                    "backup_dir": "/root/clawd_backups",
                    "retention_days": 7,
                    "max_backups": 10,
                    "schedule": {"daily": "02:00"},
                    "backup_items": [],
                    "notification": {"enabled": False},
                    "last_backup": None,
                    "backup_count": 0
                }
            }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def create_backup(self):
        """创建备份"""
        if not self.config["backup_config"]["enabled"]:
            print("备份功能已禁用")
            return False
        
        print("=" * 60)
        print("开始自动备份")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # 创建备份目录
        os.makedirs(backup_path, exist_ok=True)
        
        # 备份统计
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 备份每个项目
        for item in self.config["backup_config"]["backup_items"]:
            if not item.get("enabled", True):
                continue
            
            item_name = item["name"]
            print(f"\n📦 备份项目: {item_name}")
            
            for path in item["paths"]:
                source_path = path if path.startswith("/") else os.path.join("/root/clawd", path)
                
                if os.path.exists(source_path):
                    try:
                        # 计算目标路径
                        if path.startswith("/"):
                            # 绝对路径，保持结构
                            rel_path = path.lstrip("/")
                            dest_path = os.path.join(backup_path, rel_path)
                        else:
                            # 相对路径
                            dest_path = os.path.join(backup_path, path)
                        
                        # 创建目标目录
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        # 复制文件/目录
                        if os.path.isdir(source_path):
                            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source_path, dest_path)
                        
                        stats["success"] += 1
                        print(f"  ✅ {path}")
                    except Exception as e:
                        stats["failed"] += 1
                        print(f"  ❌ {path} - 错误: {e}")
                else:
                    stats["skipped"] += 1
                    print(f"  ⚠️  {path} - 不存在")
                
                stats["total"] += 1
        
        # 创建备份清单
        self.create_backup_manifest(backup_path, stats)
        
        # 压缩备份
        compressed_file = self.compress_backup(backup_path)
        
        # 清理旧备份
        self.cleanup_old_backups()
        
        # 更新配置
        self.config["backup_config"]["last_backup"] = datetime.now().isoformat()
        self.config["backup_config"]["backup_count"] = self.config["backup_config"].get("backup_count", 0) + 1
        self.save_config()
        
        # 发送通知
        self.send_notification(stats, compressed_file)
        
        print("\n" + "=" * 60)
        print("备份完成!")
        print(f"✅ 成功: {stats['success']}")
        print(f"⚠️  跳过: {stats['skipped']}")
        print(f"❌ 失败: {stats['failed']}")
        print(f"📦 备份文件: {os.path.basename(compressed_file)}")
        print("=" * 60)
        
        return True
    
    def create_backup_manifest(self, backup_path, stats):
        """创建备份清单"""
        manifest_file = os.path.join(backup_path, "BACKUP_MANIFEST.md")
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(f"""# 自动备份清单

## 备份信息
- **备份时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **备份名称**: {os.path.basename(backup_path)}
- **备份目录**: {backup_path}

## 备份统计
- **总项目数**: {stats['total']}
- **成功备份**: {stats['success']}
- **跳过项目**: {stats['skipped']}
- **失败项目**: {stats['failed']}

## 备份内容

### 配置文件
- AGENTS.md - AI 管家行为规范
- SOUL.md - 你的 AI 管家
- TOOLS.md - 本地工具笔记
- IDENTITY.md - 身份定义
- USER.md - 用户信息
- MEMORY.md - 记忆导航
- HEARTBEAT.md - 心跳任务
- BOOTSTRAP.md - 引导文件

### 记忆系统
- memory/ - 所有记忆文件

### 技能系统
- skills/ - 所有技能

### 脚本系统
- scripts/ - 所有脚本

### 配置管理
- config/ - 配置文件

## 恢复说明
要恢复此备份，请运行:
```bash
cd /root/clawd
tar -xzf {self.backup_dir}/{os.path.basename(backup_path)}.tar.gz --strip-components=1
```

或使用恢复脚本:
```bash
./scripts/restore_openclaw.sh {os.path.basename(backup_path)}
```

---
*自动备份系统 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""")
    
    def compress_backup(self, backup_path):
        """压缩备份"""
        print("\n📦 压缩备份文件...")
        
        compressed_file = f"{backup_path}.tar.gz"
        
        with tarfile.open(compressed_file, "w:gz") as tar:
            tar.add(backup_path, arcname=os.path.basename(backup_path))
        
        # 删除未压缩的目录
        shutil.rmtree(backup_path)
        
        # 获取压缩后大小
        size_mb = os.path.getsize(compressed_file) / (1024 * 1024)
        print(f"✅ 压缩完成: {os.path.basename(compressed_file)} ({size_mb:.2f} MB)")
        
        return compressed_file
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        retention_days = self.config["backup_config"]["retention_days"]
        max_backups = self.config["backup_config"]["max_backups"]
        
        print(f"\n🗑️  清理旧备份 (保留最近 {max_backups} 个或 {retention_days} 天内的备份)...")
        
        # 获取所有备份文件
        backup_files = []
        for file in os.listdir(self.backup_dir):
            if file.startswith("auto_backup_") and file.endswith(".tar.gz"):
                file_path = os.path.join(self.backup_dir, file)
                backup_files.append((file, os.path.getmtime(file_path)))
        
        # 按时间排序
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        deleted = 0
        for i, (file_name, mtime) in enumerate(backup_files):
            file_age_days = (time.time() - mtime) / (24 * 3600)
            
            # 删除条件：超过最大数量或超过保留天数
            if i >= max_backups or file_age_days > retention_days:
                file_path = os.path.join(self.backup_dir, file_name)
                os.remove(file_path)
                deleted += 1
                print(f"  删除: {file_name} ({file_age_days:.1f} 天前)")
        
        if deleted > 0:
            print(f"✅ 已删除 {deleted} 个旧备份")
        else:
            print("✅ 无需清理")
    
    def send_notification(self, stats, backup_file):
        """发送通知"""
        if not self.config["backup_config"]["notification"].get("enabled", False):
            return
        
        try:
            backup_name = os.path.basename(backup_file)
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            
            message = f"""📦 OpenClaw 自动备份完成

✅ 备份成功: {stats['success']} 个项目
⚠️  跳过: {stats['skipped']} 个
❌ 失败: {stats['failed']} 个

📁 备份文件: {backup_name}
📊 大小: {size_mb:.2f} MB
⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 恢复命令:
./scripts/restore_openclaw.sh {backup_name.replace('.tar.gz', '')}"""
            
            # 这里可以集成消息发送功能
            # 暂时只打印到日志
            print(f"\n📨 备份通知:\n{message}")
            
            # 保存到日志文件
            log_file = "logs/backup_notifications.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n\n")
                
        except Exception as e:
            print(f"⚠️  通知发送失败: {e}")
    
    def list_backups(self):
        """列出所有备份"""
        print("=" * 60)
        print("📋 自动备份列表")
        print("=" * 60)
        
        if not os.path.exists(self.backup_dir):
            print("备份目录不存在")
            return
        
        backup_files = []
        for file in os.listdir(self.backup_dir):
            if file.startswith("auto_backup_") and file.endswith(".tar.gz"):
                file_path = os.path.join(self.backup_dir, file)
                mtime = os.path.getmtime(file_path)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                backup_files.append((file, mtime, size_mb))
        
        if not backup_files:
            print("暂无自动备份")
            return
        
        # 按时间排序
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        for i, (file_name, mtime, size_mb) in enumerate(backup_files, 1):
            backup_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{i}. {file_name}")
            print(f"   📅 时间: {backup_time}")
            print(f"   📊 大小: {size_mb:.2f} MB")
        
        print("\n" + "=" * 60)
        print(f"总计: {len(backup_files)} 个备份")
    
    def run(self):
        """运行备份"""
        return self.create_backup()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw 自动备份系统")
    parser.add_argument("action", nargs="?", default="backup", 
                       choices=["backup", "list", "enable", "disable", "status"],
                       help="执行的操作")
    
    args = parser.parse_args()
    
    backup = AutoBackup()
    
    if args.action == "backup":
        backup.run()
    elif args.action == "list":
        backup.list_backups()
    elif args.action == "enable":
        backup.config["backup_config"]["enabled"] = True
        backup.save_config()
        print("✅ 自动备份已启用")
    elif args.action == "disable":
        backup.config["backup_config"]["enabled"] = False
        backup.save_config()
        print("⏸️  自动备份已禁用")
    elif args.action == "status":
        config = backup.config["backup_config"]
        print("=" * 60)
        print("🔧 自动备份状态")
        print("=" * 60)
        print(f"状态: {'✅ 启用' if config['enabled'] else '❌ 禁用'}")
        print(f"备份目录: {config['backup_dir']}")
        print(f"保留天数: {config['retention_days']} 天")
        print(f"最大备份数: {config['max_backups']} 个")
        print(f"上次备份: {config.get('last_backup', '从未')}")
        print(f"备份次数: {config.get('backup_count', 0)}")
        print("=" * 60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
OpenClaw 备份监控脚本
监控备份状态，发送报告
"""

import os
import json
import sys
from datetime import datetime, timedelta

def check_backup_status():
    """检查备份状态"""
    config_file = "config/backup_config.json"
    backup_dir = "/root/clawd_backups"
    
    # 加载配置
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {"backup_config": {}}
    
    # 检查备份目录
    if not os.path.exists(backup_dir):
        return {
            "status": "error",
            "message": "备份目录不存在",
            "backup_count": 0,
            "last_backup": None
        }
    
    # 获取备份文件
    backup_files = []
    for file in os.listdir(backup_dir):
        if file.endswith(".tar.gz"):
            file_path = os.path.join(backup_dir, file)
            mtime = os.path.getmtime(file_path)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            backup_files.append({
                "name": file,
                "mtime": datetime.fromtimestamp(mtime),
                "size_mb": size_mb,
                "age_days": (datetime.now() - datetime.fromtimestamp(mtime)).days
            })
    
    # 按时间排序
    backup_files.sort(key=lambda x: x["mtime"], reverse=True)
    
    # 检查最近备份
    last_backup = backup_files[0] if backup_files else None
    
    # 判断状态
    if not backup_files:
        status = "error"
        message = "暂无备份文件"
    elif last_backup["age_days"] > 2:
        status = "warning"
        message = f"最近备份是 {last_backup['age_days']} 天前"
    else:
        status = "ok"
        message = "备份正常"
    
    return {
        "status": status,
        "message": message,
        "backup_count": len(backup_files),
        "last_backup": last_backup["mtime"].isoformat() if last_backup else None,
        "recent_backups": [
            {
                "name": b["name"],
                "time": b["mtime"].isoformat(),
                "size_mb": b["size_mb"],
                "age_days": b["age_days"]
            }
            for b in backup_files[:3]  # 最近3个备份
        ]
    }

def generate_report():
    """生成备份报告"""
    status = check_backup_status()
    
    report = f"""📊 OpenClaw 备份监控报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 状态: {status['status'].upper()}
📝 消息: {status['message']}

📦 备份统计:
   • 总备份数: {status['backup_count']}
   • 最近备份: {status['last_backup'] or '无'}

📋 最近备份:
"""
    
    if status['recent_backups']:
        for i, backup in enumerate(status['recent_backups'], 1):
            report += f"   {i}. {backup['name']}\n"
            report += f"      时间: {backup['time']}\n"
            report += f"      大小: {backup['size_mb']:.2f} MB\n"
            report += f"      天数: {backup['age_days']} 天前\n"
    else:
        report += "   暂无备份\n"
    
    report += f"""
🔧 自动备份配置:
   • 每日备份: 02:00 (cron)
   • 每周完整备份: 周日 03:00
   • 保留策略: 7天或最多10个备份

💡 建议:
"""
    
    if status['status'] == 'error':
        report += "   • 立即运行手动备份\n"
        report += "   • 检查备份脚本权限\n"
        report += "   • 验证备份目录可写\n"
    elif status['status'] == 'warning':
        report += "   • 检查cron服务是否运行\n"
        report += "   • 查看备份日志文件\n"
    else:
        report += "   • 备份系统运行正常\n"
        report += "   • 建议定期验证恢复功能\n"
    
    return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw 备份监控")
    parser.add_argument("action", nargs="?", default="report", 
                       choices=["report", "status", "check"],
                       help="执行的操作")
    
    args = parser.parse_args()
    
    if args.action == "report":
        report = generate_report()
        print(report)
        
        # 保存报告到文件
        report_file = "logs/backup_monitor_report.md"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 报告已保存到: {report_file}")
        
    elif args.action == "status":
        status = check_backup_status()
        print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
        
    elif args.action == "check":
        status = check_backup_status()
        if status['status'] in ['error', 'warning']:
            print(f"❌ 备份状态异常: {status['message']}")
            sys.exit(1)
        else:
            print(f"✅ 备份状态正常: {status['message']}")
            sys.exit(0)

if __name__ == "__main__":
    main()
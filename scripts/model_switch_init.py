#!/usr/bin/env python3
"""
模型切换后的初始化脚本
确保切换模型后还能记住 skills 和定时任务
"""

import os
import json
import sys
from datetime import datetime

def load_agent_config():
    """加载代理配置"""
    config_path = "config/agent_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"agent_config": {}}

def save_agent_config(config):
    """保存代理配置"""
    config_path = "config/agent_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def update_model_info(new_model):
    """更新模型信息"""
    config = load_agent_config()
    
    if "agent_config" not in config:
        config["agent_config"] = {}
    
    config["agent_config"]["current_model"] = new_model
    config["agent_config"]["last_model_switch"] = datetime.utcnow().isoformat() + "Z"
    
    save_agent_config(config)
    print(f"✅ 已更新模型配置: {new_model}")

def get_available_skills():
    """获取可用的 skills 列表"""
    skills_dir = "skills"
    qqbot_skills_dir = os.path.expanduser("~/.openclaw/extensions/openclaw-qqbot/skills")
    
    skills = []
    
    # 获取主要 skills
    if os.path.exists(skills_dir):
        for item in os.listdir(skills_dir):
            if os.path.isdir(os.path.join(skills_dir, item)):
                skills.append(item)
    
    # 获取 QQBot skills
    if os.path.exists(qqbot_skills_dir):
        for item in os.listdir(qqbot_skills_dir):
            if os.path.isdir(os.path.join(qqbot_skills_dir, item)):
                skills.append(item)
    
    return sorted(skills)

def update_skills_list():
    """更新 skills 列表"""
    config = load_agent_config()
    
    if "agent_config" not in config:
        config["agent_config"] = {}
    
    skills = get_available_skills()
    config["agent_config"]["available_skills"] = skills
    config["agent_config"]["skills_last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    save_agent_config(config)
    print(f"✅ 已更新 skills 列表: {len(skills)} 个 skills")
    return skills

def get_scheduled_tasks():
    """获取定时任务列表"""
    # 这里可以集成 qqbot-cron 技能
    # 暂时返回空列表，实际使用时可以读取定时任务文件
    return []

def initialize_after_model_switch(new_model=None):
    """模型切换后的初始化"""
    print("=" * 60)
    print("模型切换初始化")
    print("=" * 60)
    
    # 1. 更新模型信息
    if new_model:
        update_model_info(new_model)
    
    # 2. 更新 skills 列表
    skills = update_skills_list()
    
    # 3. 获取定时任务
    tasks = get_scheduled_tasks()
    
    # 4. 生成初始化报告
    config = load_agent_config()
    
    print("\n📋 初始化完成:")
    print(f"• 当前模型: {config['agent_config'].get('current_model', '未知')}")
    print(f"• 可用 skills: {len(skills)} 个")
    print(f"• 定时任务: {len(tasks)} 个")
    
    print("\n🔧 可用 skills 列表:")
    for i, skill in enumerate(skills, 1):
        print(f"  {i:2d}. {skill}")
    
    print("\n💡 提示: 所有配置已保存到 config/agent_config.json")
    print("=" * 60)
    
    return {
        "model": config['agent_config'].get('current_model'),
        "skills": skills,
        "tasks": tasks,
        "config_file": "config/agent_config.json"
    }

if __name__ == "__main__":
    # 命令行使用
    if len(sys.argv) > 1:
        new_model = sys.argv[1]
        initialize_after_model_switch(new_model)
    else:
        initialize_after_model_switch()
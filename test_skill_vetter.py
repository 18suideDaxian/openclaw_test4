#!/usr/bin/env python3
"""
测试 skill-vetter 技能
"""

import os
import json

def test_skill_vetter():
    """测试 skill-vetter 技能"""
    
    print("=" * 60)
    print("测试 skill-vetter 技能")
    print("=" * 60)
    
    # 检查技能目录
    skill_path = "skills/skill-vetter"
    if not os.path.exists(skill_path):
        print(f"❌ 技能目录不存在: {skill_path}")
        return
    
    print(f"✅ 技能目录存在: {skill_path}")
    
    # 检查 SKILL.md 文件
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_md):
        print(f"✅ SKILL.md 文件存在")
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   文件大小: {len(content)} 字节")
            print(f"   包含 'Skill Vetter' 标题: {'Skill Vetter' in content}")
            print(f"   包含安全检查内容: {'RED FLAGS' in content}")
    else:
        print(f"❌ SKILL.md 文件不存在")
    
    # 检查 _meta.json 文件
    meta_json = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_json):
        print(f"✅ _meta.json 文件存在")
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            print(f"   技能名称: {meta.get('slug', 'N/A')}")
            print(f"   版本: {meta.get('version', 'N/A')}")
    else:
        print(f"❌ _meta.json 文件不存在")
    
    print("\n" + "=" * 60)
    print("skill-vetter 技能概述:")
    print("-" * 60)
    
    # 显示技能描述
    with open(skill_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("description:"):
                print(f"描述: {line.split(':', 1)[1].strip()}")
            if line.startswith("# Skill Vetter"):
                print(f"标题: {line.strip()}")
                # 显示前几行描述
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        print(f"简介: {lines[j].strip()}")
                        break
                break
    
    print("\n" + "=" * 60)
    print("技能功能验证:")
    print("-" * 60)
    
    # 验证技能的关键功能
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 检查关键部分
        sections = [
            ("Vetting Protocol", "是否包含审查协议"),
            ("RED FLAGS", "是否包含红色警告列表"),
            ("Risk Classification", "是否包含风险分类"),
            ("Output Format", "是否包含输出格式"),
            ("Quick Vet Commands", "是否包含快速审查命令"),
        ]
        
        for section, description in sections:
            if section in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
    
    print("\n" + "=" * 60)
    print("技能应用测试:")
    print("-" * 60)
    
    # 模拟使用 skill-vetter 审查另一个技能
    print("模拟审查 'word-docx' 技能:")
    print("1. ✅ 检查来源: ClawHub (已知来源)")
    print("2. ✅ 检查作者: 已知作者")
    print("3. ✅ 检查文件: 包含 SKILL.md 和脚本文件")
    print("4. ✅ 检查权限: 仅处理 Word 文档，无危险权限")
    print("5. ✅ 检查代码: 无红色警告")
    print("\n审查结果: 🟢 LOW 风险")
    print("建议: ✅ SAFE TO INSTALL")

if __name__ == "__main__":
    test_skill_vetter()
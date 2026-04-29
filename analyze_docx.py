#!/usr/bin/env python3
import sys
from docx import Document

def analyze_docx_paragraphs(docx_path):
    """分析 Word 文档的段落结构"""
    try:
        doc = Document(docx_path)
        
        print("=" * 60)
        print(f"分析文档: {docx_path}")
        print("=" * 60)
        
        # 获取所有段落
        paragraphs = doc.paragraphs
        print(f"文档中的段落数量: {len(paragraphs)}")
        print()
        
        # 分析每个段落
        for i, para in enumerate(paragraphs, 1):
            text = para.text.strip()
            if text:  # 只显示非空段落
                print(f"段落 {i}:")
                print(f"  文本内容: '{text}'")
                print(f"  文本长度: {len(text)} 字符")
                print(f"  原始文本 (包含换行符): {repr(para.text)}")
                
                # 检查段落样式
                style = para.style.name if para.style else "无样式"
                print(f"  段落样式: {style}")
                
                # 检查段落格式
                if para.alignment:
                    print(f"  对齐方式: {para.alignment}")
                
                # 检查是否有换行符
                if '\n' in para.text:
                    print(f"  包含换行符: 是")
                    # 显示换行符位置
                    lines = para.text.split('\n')
                    print(f"  分割为 {len(lines)} 行:")
                    for j, line in enumerate(lines, 1):
                        print(f"    行 {j}: '{line.strip()}'")
                else:
                    print(f"  包含换行符: 否")
                
                print("-" * 40)
        
        # 分析段落分隔符
        print("\n段落分隔分析:")
        all_text = "\n".join([para.text for para in paragraphs])
        
        # 检查文档中是否包含连续换行符
        double_newlines = all_text.count('\n\n')
        print(f"文档中双换行符 ('\\n\\n') 的数量: {double_newlines}")
        
        # 检查段落之间的实际分隔
        print("\n段落之间的分隔:")
        for i in range(len(paragraphs) - 1):
            para1 = paragraphs[i].text.strip()
            para2 = paragraphs[i + 1].text.strip()
            if para1 and para2:
                print(f"段落 {i+1} 和段落 {i+2} 之间: 有内容分隔")
            elif not para1 and para2:
                print(f"段落 {i+1} 和段落 {i+2} 之间: 空段落分隔")
        
        # 提取所有文本（模拟不同处理方式）
        print("\n不同方式提取的文本对比:")
        
        # 方式1: 简单连接（可能有问题）
        simple_text = ""
        for para in paragraphs:
            if para.text.strip():
                simple_text += para.text + "\n"
        print("方式1 (简单连接):")
        print(f"  段落数: {len([p for p in paragraphs if p.text.strip()])}")
        print(f"  文本长度: {len(simple_text)}")
        
        # 方式2: 按照双换行符分隔
        combined_text = "\n".join([para.text for para in paragraphs])
        paragraphs_by_double_newline = [p.strip() for p in combined_text.split('\n\n') if p.strip()]
        print("\n方式2 (按双换行符分割):")
        print(f"  段落数: {len(paragraphs_by_double_newline)}")
        for i, para in enumerate(paragraphs_by_double_newline, 1):
            if i <= 3:  # 只显示前3个
                print(f"  段落 {i}: '{para[:50]}...'")
        
        # 方式3: 按照单换行符分隔
        paragraphs_by_single_newline = [p.strip() for p in combined_text.split('\n') if p.strip()]
        print("\n方式3 (按单换行符分割):")
        print(f"  段落数: {len(paragraphs_by_single_newline)}")
        for i, para in enumerate(paragraphs_by_single_newline, 1):
            if i <= 3:  # 只显示前3个
                print(f"  段落 {i}: '{para[:50]}...'")
        
    except Exception as e:
        print(f"分析文档时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = "/root/.openclaw/qqbot/downloads/table_1776066942731.docx"
    
    analyze_docx_paragraphs(docx_path)